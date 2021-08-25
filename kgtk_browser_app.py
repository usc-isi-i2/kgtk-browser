"""
Kypher backend support for the KGTK browser.
"""

import hashlib
from http import HTTPStatus
import os.path
import sys
import traceback
import typing
import urllib.parse

import flask
import browser.backend.kypher as kybe

from kgtk.kgtkformat import KgtkFormat
from kgtk.value.kgtkvalue import KgtkValue, KgtkValueFields


# How to run:
# > export FLASK_APP=kgtk_browser_app.py
# > export FLASK_ENV=development
# > export KGTK_BROWSER_CONFIG=$PWD/kgtk_browser_config.py
# > flask run

# Example invocation:
# http://127.0.0.1:5000/kgtk/browser/backend/get_all_node_data?node=Q5


### Flask application

app = flask.Flask(__name__,
                  static_url_path='',
                  static_folder='web/static',
                  template_folder='web/templates')
app.config.from_envvar('KGTK_BROWSER_CONFIG')

DEFAULT_SERVICE_PREFIX = '/kgtk/browser/backend/'
DEFAULT_LANGUAGE = 'en'

app.config['SERVICE_PREFIX'] = app.config.get('SERVICE_PREFIX', DEFAULT_SERVICE_PREFIX)
app.config['DEFAULT_LANGUAGE'] = app.config.get('DEFAULT_LANGUAGE', DEFAULT_LANGUAGE)

app.kgtk_backend = kybe.BrowserBackend(app)

def get_backend(app):
    return app.kgtk_backend


### Multi-threading

# Proper locking is now supported by the backend like this:

"""
with get_backend(app) as backend:
    edges = backend.get_node_edges(node)
    ...
"""

# Ringgaard browser support:
@app.route('/kb', methods=['GET'])
def rb_get_kb():
    return flask.send_from_directory('web/static', 'kb.html')

@app.route('/kb/query', methods=['GET'])
def rb_get_kb_query():
    q = flask.request.args.get('q')
    print("rb_get_kb_query: " + q)

    try:
        with get_backend(app) as backend:
            matches = [ ]

            results = backend.rb_get_nodes_starting_with(q, lang="en")
            for result in results:
                item = result[0]
                label = KgtkFormat.unstringify(result[1])
                matches.append(
                    {
                        "ref": item,
                        "text": item,
                        "description": label
                    }
                )
            response_data = {
                "matches": matches
            }
            
            return flask.jsonify(response_data), 200
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)


def rb_link_to_url(text_value, current_value, lang: str = "en", prop: typing.Optional[str] = None)->bool:
    if text_value is None:
        return False

    # Look for text strings that are URLs:
    if text_value.startswith(("https://", "http://")):
        # print("url spotted: %s" % repr(text_value)) # ***
        current_value["url"] = text_value
        return True

    elif text_value.endswith((".jpg", ".svg")):
        image_url: str = "https://commons.wikimedia.org/wiki/File:"  + text_value
        # print("image spotted: %s" % repr(image_url)) # ***
        current_value["url"] = image_url
        return True
    return False

def rb_unstringify(item: str, default: str = "")->str:
    return KgtkFormat.unstringify(item) if item is not None and len(item) > 0 else default

rb_image_formatter_cache: typing.MutableMapping[str, typing.Optional[str]] = dict()

def get_image_formatter(backend, relationship: str)->typing.Optional[str]:
    if relationship not in rb_image_formatter_cache:
        result: typing.List[typing.List[str]] = backend.rb_get_image_formatter(relationship)
        if len(result) == 0:
            rb_image_formatter_cache[relationship] = None
        else:
            rb_image_formatter_cache[relationship] = rb_unstringify(result[0][0])
    return rb_image_formatter_cache[relationship]

rb_units_node_cache: typing.MutableMapping[str, typing.Optional[str]] = dict()

def rb_build_current_value(backend,
                           target_node: str,
                           value: KgtkValue,
                           rb_type: str,
                           target_node_label: typing.Optional[str],
                           target_node_description: typing.Optional[str],
                           lang: str,
                           relationship: str = "",
                           wikidatatype: str = ""
                           )->typing.Mapping[str, str]:
    current_value: typing.MutableMapping[str, any] = dict()
    datatype: KgtkFormat.DataType = value.classify()

    text_value: str
    
    if wikidatatype == "external-id":
        text_value = rb_unstringify(target_node)
        current_value["text"] = text_value
        formatter: typing.Optional[str] = get_image_formatter(backend, relationship)
        if formatter is not None:
            # print("formatter: %s" % formatter, file=sys.stderr, flush=True) # ***
            current_value["url"] = formatter.replace("$1", text_value)
        else:
            rb_link_to_url(text_value, current_value)

    elif rb_type == "/w/item":
        current_value["ref"] = target_node
        current_value["text"] = rb_unstringify(target_node_label, default=target_node)
        current_value["description"] = rb_unstringify(target_node_description, default=target_node)

    elif rb_type == "/w/text":
        language: str
        language_suffix: str
        text_value, language, language_suffix = KgtkFormat.destringify(target_node)
        current_value["text"] = text_value
        current_value["lang"] = language + language_suffix
        rb_link_to_url(text_value, current_value, lang=language)

    elif rb_type == "/w/string":
        text_value = rb_unstringify(target_node)
        current_value["text"] = text_value
        rb_link_to_url(text_value, current_value)

    elif rb_type == "/w/quantity":
        if datatype == KgtkFormat.DataType.NUMBER:
            numberstr: str = target_node
            if numberstr.startswith("+"): # Reamove any leading "+"
                numberstr = numberstr[1:]
            current_value["text"] = numberstr
        else:
            if value.parse_fields():
                newnum: str = value.fields.numberstr
                if newnum.startswith("+"): # Remove any leading "+"
                    newnum = newnum[1:]
                if value.fields.low_tolerancestr is not None or value.fields.high_tolerancestr is not None:
                    newnum += "["
                    if value.fields.low_tolerancestr is not None:
                        newnum += value.fields.low_tolerancestr
                    newnum += ","
                    if value.fields.high_tolerancestr is not None:
                        newnum += value.fields.high_tolerancestr
                    newnum += "]"
                if value.fields.si_units is not None:
                    newnum += value.fields.si_units
                if value.fields.units_node is not None:
                    # Here's where it gets fancy:
                    units_node: str = value.fields.units_node
                    if units_node not in rb_units_node_cache:
                        units_node_labels: typing.List[typing.List[str]] = backend.get_node_labels(units_node, lang=lang)
                        if len(units_node_labels) > 0:
                            units_node_label: str = units_node_labels[0][1]
                            rb_units_node_cache[units_node] = rb_unstringify(units_node_label)
                        else:
                            rb_units_node_cache[units_node] = None # Remember the failure.
                                       
                    if rb_units_node_cache[units_node] is not None:
                        newnum += " " + rb_units_node_cache[units_node]
                    else:
                        newnum += " " + units_node # We could not find a label for this node when we looked last time.
                    current_value["ref"] = units_node

                current_value["text"] = newnum
            else:
                # Validation failed.
                #
                # TODO: Add a validation failure indicator?
                current_value["text"] = target_node

    elif rb_type == "/w/time":
        if value.parse_fields() and value.fields.precision is not None:
            f: KgtkValueFields = value.fields
            precision: int = f.precision
            if precision <= 9 and f.yearstr is not None:
                current_value["text"] = f.yearstr
            elif precision == 10 and f.yearstr is not None and f.monthstr is not None:
                 current_value["text"] = f.yearstr + "-" + f.monthstr
            elif precision == 11 and f.yearstr is not None and f.monthstr is not None and f.daystr is not None:
                 current_value["text"] = f.yearstr + "-" + f.monthstr + "-" + f.daystr
            elif precision == 12 and f.yearstr is not None and f.monthstr is not None and f.daystr is not None and f.hourstr is not None and f.minutesstr is not None:
                 current_value["text"] = f.yearstr + "-" + f.monthstr + "-" + f.daystr + " " + f.hourstr + ":" + f.minutesstr
            elif precision == 13 and f.yearstr is not None and f.monthstr is not None and f.daystr is not None and f.hourstr is not None and f.minutesstr is not None:
                 current_value["text"] = f.yearstr + "-" + f.monthstr + "-" + f.daystr + " " + f.hourstr + ":" + f.minutesstr
            else:
                current_value["text"] = target_node[1:]
        else:
            # Validation failed.
            #
            # TODO: Add a validation failure indicator?
            current_value["text"] = target_node[1:]
            
        
    elif rb_type == "/w/geo":
        geoloc = target_node[1:]
        current_value["text"] = geoloc # Consider reformatting
        current_value["url"] = "http://maps.google.com/maps?q=" + geoloc.replace("/", ",")
    else:
        print("*** unknown rb_type %s" % repr(rb_type)) # ***

    return current_value

def rb_find_type(node2: str, value: KgtkValue)->str:
    datatype: KgtkFormat.DataType = value.classify()
    rb_type: str

    if datatype == KgtkFormat.DataType.SYMBOL:
        if node2 is not None and node2.startswith(("P", "Q")):
            rb_type = "/w/item"
        else:
            rb_type = "unknown"
            print("*** unknown datatype: no node2") # ***def rb_send_kb_item(item: str):
            
    elif datatype == KgtkFormat.DataType.LANGUAGE_QUALIFIED_STRING:
        rb_type = "/w/text"
    elif datatype == KgtkFormat.DataType.STRING:
        rb_type = "/w/string"
    elif datatype == KgtkFormat.DataType.QUANTITY:
        rb_type = "/w/quantity"
    elif datatype == KgtkFormat.DataType.NUMBER:
        rb_type = "/w/quantity"
    elif datatype == KgtkFormat.DataType.DATE_AND_TIMES:
        rb_type = "/w/time"
    elif datatype == KgtkFormat.DataType.LOCATION_COORDINATES:
        rb_type = "/w/geo"
    else:
        rb_type = "/w/unknown" # Includes EMPTY, LIST, EXTENSION, BOOLEAN
        print("*** unknown datatype") # ***def rb_send_kb_item(item: str):
    return rb_type

# The following routine was taken from Stack Overflow.
# https://stackoverflow.com/questions/33689980/get-thumbnail-image-from-wikimedia-commons
def rb_get_wc_thumb(image: str, width: int = 300): # image = e.g. from Wikidata, width in pixels
    image = image.replace(' ', '_') # need to replace spaces with underline 
    m = hashlib.md5()
    m.update(image.encode('utf-8'))
    d: str = m.hexdigest()
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/"+d[0]+'/'+d[0:2]+'/'+image+'/'+str(width)+'px-'+image

def rb_build_gallery(item_edges: typing.List[typing.List[str]],
                     item: str,
                     item_labels: typing.List[typing.List[str]])->typing.List[typing.Mapping[str, str]]:
    gallery: typing.List[typing.List[str]] = list()

    item_edge: typing.List[str]
    for item_edge in item_edges:
        edge_id: str
        node1: str
        relationship: str
        node2: str
        relationship_label: typing.Optional[str]
        target_node: str
        target_label: typing.Optional[str]
        target_description: typing.Optional[str]
        wikidatatype: typing.Optional[str]
        edge_id, node1, relationship, node2, relationship_label, target_node, target_label, target_description, wikidatatype = item_edge

        if relationship == "P18":
            value: KgtkValue = KgtkValue(node2)
            if value.is_string() or value.is_language_qualified_string():
                new_image: typing.Mapping[str, str] = {
                    "url": rb_get_wc_thumb(rb_unstringify(node2)),
                    "text": rb_unstringify(item_labels[0][1]) if len(item_labels) > 0 else item
                }
                # print("new image: %s" % repr(new_image), file=sys.stderr, flush=True)
                gallery.append(new_image)

    # print("gallery: %s" % repr(gallery), file=sys.stderr, flush=True)

    return gallery    


# List the properties in the order that you want them to appear.  All unlisted
# properties will appear after these.  The list may include 
rb_property_priority_list: typing.List[str] = [
    "P31",
    "P231",
]

rb_property_priority_map: typing.Mapping[str, int] = { val: idx for idx, val in enumerate(rb_property_priority_list) }

def rb_build_keyed_item_edges(item_edges: typing.List[typing.List[str]])->typing.MutableMapping[str, typing.List[str]]:
    # Sort the item edges
    keyed_item_edges: typing.MutableMapping[str, typing.List[str]] = dict()

    idx: int
    item_edge: typing.List[str]
    for idx, item_edge in enumerate(item_edges):
        edge_id, node1, relationship, node2, relationship_label, target_node, target_label, target_description, wikidatatype = item_edge
        if relationship_label is None:
            relationship_label = ""
        if target_label is None:
            target_label = target_node
            priority: int = rb_property_priority_map.get(relationship, 99999)
        item_edge_key: str = (str(priority+100000) + "|" + relationship_label + "|" + target_label + "|" + str(idx + 1000000)).lower()
        keyed_item_edges[item_edge_key] = item_edge
    return keyed_item_edges

def rb_build_item_qualifier_map(item_qualifier_edges: typing.List[typing.List[str]])->typing.MutableMapping[str, typing.List[typing.List[str]]]:
    item_qual_map: typing.MutableMapping[str, typing.List[typing.List[str]]] = dict()
    item_qual_edge: typing.List[str]
    for item_qual_edge in item_qualifier_edges:
        edge_id: str = item_qual_edge[0]
        if edge_id not in item_qual_map:
            item_qual_map[edge_id] = list()
        item_qual_map[edge_id].append(item_qual_edge)
    return item_qual_map

def rb_send_kb_items_and_qualifiers(backend,
                                    item: str,
                                    response_properties: typing.MutableMapping[str, any],
                                    response_xrefs: typing.MutableMapping[str, any],
                                    item_edges: typing.List[typing.List[str]],
                                    item_qualifier_edges: typing.List[typing.List[str]],
                                    lang: str = 'en',
                                    verbose: bool = False):

    item_qual_map: typing.MutableMapping[str, typing.List[typing.List[str]]] = rb_build_item_qualifier_map(item_qualifier_edges)

    current_edge_id: typing.Optional[str] = None
    current_relationship: typing.Optional[str] = None
    current_property_map: typing.MutableMapping[str, any] = dict()
    current_values: typing.List[typing.MutableMapping[str, any]] = list()
    current_node2: typing.Optional[str] = None

    # Sort the item edges
    keyed_item_edges: typing.MutableMapping[str, typing.List[str]] = rb_build_keyed_item_edges(item_edges)

    item_edge_key: str
    for item_edge_key in sorted(keyed_item_edges.keys()):
        item_edge: typing.List[str] = keyed_item_edges[item_edge_key]
        if verbose:
            print(repr(item_edge), file=sys.stderr, flush=True)

        edge_id: str
        node1: str
        relationship: str
        node2: str
        relationship_label: typing.Optional[str]
        target_node: str
        target_label: typing.Optional[str]
        target_description: typing.Optional[str]
        wikidatatype: typing.Optional[str]
        edge_id, node1, relationship, node2, relationship_label, target_node, target_label, target_description, wikidatatype = item_edge

        if current_edge_id is not None and current_edge_id == edge_id:
            if verbose:
                print("*** skipping duplicate %s" % repr(current_edge_id), file=sys.stderr, flush=True)
            # Skip duplicates (say, multiple labels or descriptions).
            continue
        current_edge_id = edge_id

        value: KgtkValue = KgtkValue(target_node)
        rb_type: str = rb_find_type(target_node, value)
                
        if current_relationship is None or relationship != current_relationship:
            current_relationship = relationship
            current_property_map = dict()
            if wikidatatype is not None and wikidatatype == "external-id":
                response_xrefs.append(current_property_map)
            else:
                response_properties.append(current_property_map)
            current_property_map["ref"] = relationship
            current_property_map["property"] = rb_unstringify(relationship_label, default=relationship)
            current_property_map["type"] = rb_type # TODO: check for consistency
            current_values = list()
            current_property_map["values"] = current_values

        current_value: typing.MutableMapping[str, any] = rb_build_current_value(backend,
                                                                                target_node,
                                                                                value,
                                                                                rb_type,
                                                                                target_label,
                                                                                target_description,
                                                                                lang,
                                                                                relationship,
                                                                                wikidatatype)
        current_values.append(current_value)

        if edge_id in item_qual_map:
            current_qual_edge_id: typing.Optional[str] = None
            current_qual_relationship: typing.Optional[str] = None
            current_qual_property_map: typing.MutableMapping[str, any] = dict()
            current_qual_node2: typing.Optional[str] = None
            current_qualifiers: typing.List[typing.MutableMapping[str, any]] = list()
            current_value["qualifiers"] = current_qualifiers

            qual_relationship: str
            qual_node2: str
            qual_relationship_label: typing.Optional[str]
            qual_node2_label: typing.Optional[str]
            qual_node2_description: typing.Optional[str]
                    
            for item_qual_edge in item_qual_map[edge_id]:
                if verbose:
                    print(repr(item_qual_edge), file=sys.stderr, flush=True)

                qual_edge_id: str
                _, node1, qual_edge_id, qual_relationship, qual_node2, qual_relationship_label, qual_node2_label, qual_node2_description = item_qual_edge
                        
                if current_qual_edge_id is not None and current_qual_edge_id == qual_edge_id:
                    if verbose:
                        print("*** skipping duplicate qualifier %s" % repr(current_qual_edge_id), file=sys.stderr, flush=True)
                    # Skip duplicates (say, multiple labels or descriptions).
                    continue
                current_qual_edge_id = qual_edge_id
                        
                qual_value: KgtkValue = KgtkValue(qual_node2)
                qual_rb_type: str = rb_find_type(qual_node2, qual_value)

                if current_qual_relationship is None or qual_relationship != current_qual_relationship:
                    current_qual_relationship = qual_relationship
                    current_qual_property_map = dict()
                    current_qualifiers.append(current_qual_property_map)
                    current_qual_property_map["ref"] = qual_relationship
                    current_qual_property_map["property"] = rb_unstringify(qual_relationship_label, default=qual_relationship)
                    current_qual_property_map["type"] = qual_rb_type # TODO: check for consistency
                    current_qual_values = list()
                    current_qual_property_map["values"] = current_qual_values
                    
                current_qual_value: typing.MutableMapping[str, any] = rb_build_current_value(backend,
                                                                                             qual_node2,
                                                                                             qual_value,
                                                                                             qual_rb_type,
                                                                                             qual_node2_label,
                                                                                             qual_node2_description,
                                                                                             lang)
                current_qual_values.append(current_qual_value)

def rb_send_kb_categories(backend,
                          item: str,
                          response_categories: typing.MutableMapping[str, any],
                          category_edges: typing.List[typing.List[str]],
                          lang: str = 'en',
                          verbose: bool = False):

    if verbose:
        print("#categories: %d" % len(category_edges), file=sys.stderr, flush=True)

    node1: str
    node1_label: str
    node1_description: str

    categories_seen: typing.Set[str] = set()

    # Sort the item categories
    category_key: str
    keyed_category_edges: typing.MutableMapping[str, typing.List[str]] = dict()
    idx: int
    category_edge: typing.List[str]
    for idx, category_edge in enumerate(category_edges):
        node1, node1_label, node1_description = category_edge
        if node1 in categories_seen:
            continue
        categories_seen.add(node1)
        
        if node1_label is None:
            node1_label = node1
        category_key = (node1_label + "|" + str(idx + 1000000)).lower()
        keyed_category_edges[category_key] = category_edge

    for category_key in sorted(keyed_category_edges.keys()):
        category_edge = keyed_category_edges[category_key]
        if verbose:
            print(repr(category_edge), file=sys.stderr, flush=True)
        node1, node1_label, node1_description = category_edge

        response_categories.append(
            {
                "ref": node1,
                "text": rb_unstringify(node1_label, default=node1),
                "description": rb_unstringify(node1_description, default=node1)
            }
        )


def rb_send_kb_item(item: str):
    lang: str = 'en'
    verbose: bool = False
    
    try:
        with get_backend(app) as backend:
            if verbose or True:
                print("Fetching item edges", file=sys.stderr, flush=True) # ***
            item_edges: typing.List[typing.List[str]] = backend.rb_get_node_edges(item, lang=lang)
            if verbose or True:
                print("Fetching qualifier edges", file=sys.stderr, flush=True) # ***
            item_qualifier_edges: typing.List[typing.List[str]] = backend.rb_get_node_edge_qualifiers(item, lang=lang)
            # item_inverse_edges: typing.List[typing.List[str]] = backend.rb_get_node_inverse_edges(item, lang=lang)
            # item_inverse_qualifier_edges: typing.List[typing.List[str]] = backend.rb_get_node_inverse_edge_qualifiers(item, lang=lang)
            # if verbose:
            #     print("Fetching category edges", file=sys.stderr, flush=True) # ***
            # item_category_edges: typing.List[typing.List[str]] = backend.rb_get_node_categories(item, lang=lang)
            if verbose or True:
                print("Done fetching edges", file=sys.stderr, flush=True) # ***

            response: typing.MutableMapping[str, any] = dict()
            response["ref"] = item

            item_labels: typing.List[typing.List[str]] = backend.get_node_labels(item, lang=lang)
            response["text"] = rb_unstringify(item_labels[0][1]) if len(item_labels) > 0 else item

            item_descriptions: typing.List[typing.List[str]] = backend.get_node_descriptions(item, lang=lang)
            response["description"] = rb_unstringify(item_descriptions[0][1]) if len(item_descriptions) > 0 else item

            response_properties: typing.List[typing.MutableMapping[str, any]] = [ ]
            response["properties"] = response_properties
            response_xrefs: typing.List[typing.MutableMapping[str, any]] = [ ]
            response["xrefs"] = response_xrefs
            rb_send_kb_items_and_qualifiers(backend, item, response_properties, response_xrefs, item_edges, item_qualifier_edges, lang=lang, verbose=verbose)

            # response_categories: typing.List[typing.MutableMapping[str, any]] = [ ]
            # response["categories"] = response_categories
            # rb_send_kb_categories(backend, item, response_categories, item_category_edges, lang=lang, verbose=verbose)

            # We cound assume a link to Wikipedia, but that won't be valid when
            # using KGTK for other data sources.
            # response["url"] = "https://sample.url"
            # response["document"] = "Sample document: " + item

            # The data source would also, presumably, be responsible for providing images.
            # response["gallery"] = [ ] # This is required by kb.js as a minimum element.
            response["gallery"] = rb_build_gallery(item_edges, item, item_labels)

            return flask.jsonify(response), 200
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_exc()
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route('/kb/item', methods=['GET'])
def rb_get_kb_item():
    item = flask.request.args.get('id')
    print("rb_get_kb_item: " + item)
    return rb_send_kb_item(item)


@app.route('/kb/<string:item>', methods=['GET'])
def rb_get_kb_named_item(item):
    print("get_kb_named_item: " + item)
    if item is None or len(item) == 0:
        try:
            return flask.send_from_directory('web/static', "kb.html")
        except Exception as e:
            print('ERROR: ' + str(e))
            flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
        
    elif item.startswith(("Q", "P")):
        try:
            return flask.render_template("kb.html", ITEMID=item)
        except Exception as e:
            print('ERROR: ' + str(e))
            flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

    elif item in [ "kb.js", "kb.html" ]:
        try:
            return flask.send_from_directory('web/static', item)
        except Exception as e:
            print('ERROR: ' + str(e))
            flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

    else:
        print("Unrecognized item: %s" % repr(item))
        flask.abort(400, "Unrecognized item %s" % repr(item))
            
    


### Test URL handlers:

# These all call the corresponding backend query method with the same name.
# Use 'fmt=df' for the most readable output, however, that requires pandas
# to be installed.  Otherwise a pretty-printed list format is the default.

# Status codes: https://docs.python.org/3/library/http.html

def get_request_args():
    """Access all handler args we currently support.
    """
    return {
        'node': flask.request.args.get('node'),
        'lang': flask.request.args.get('lang', app.config['DEFAULT_LANGUAGE']),
        'images': flask.request.args.get('images', 'False').lower() == 'true',
        'fanouts': flask.request.args.get('fanouts', 'False').lower() == 'true',
        'inverse': flask.request.args.get('inverse', 'False').lower() == 'true',
        'fmt': flask.request.args.get('fmt'),
    }

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'test_get_edges'), methods=['GET'])
def test_get_edges():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    return 'get_edges %s ' % node

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_labels'), methods=['GET'])
def get_node_labels():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            labels = backend.get_node_labels(args['node'], lang=args['lang'], fmt=args['fmt'])
            return backend.query_result_to_string(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_aliases'), methods=['GET'])
def get_node_aliases():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            aliases = backend.get_node_aliases(args['node'], lang=args['lang'], fmt=args['fmt'])
            return backend.query_result_to_string(aliases)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_descriptions'), methods=['GET'])
def get_node_descriptions():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            descriptions = backend.get_node_descriptions(args['node'], lang=args['lang'], fmt=args['fmt'])
            return backend.query_result_to_string(descriptions)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_images'), methods=['GET'])
def get_node_images():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            images = backend.get_node_images(args['node'], fmt=args['fmt'])
            return backend.query_result_to_string(images)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edges'), methods=['GET'])
def get_node_edges():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            edges = backend.get_node_edges(
                args['node'], lang=args['lang'], images=args['images'], fanouts=args['fanouts'], fmt=args['fmt'])
            return backend.query_result_to_string(edges)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_inverse_edges'), methods=['GET'])
def get_node_inverse_edges():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            edges = backend.get_node_inverse_edges(
                args['node'], lang=args['lang'], images=args['images'], fanouts=args['fanouts'], fmt=args['fmt'])
            return backend.query_result_to_string(edges)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_qualifiers'), methods=['GET'])
def get_node_edge_qualifiers():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            qualifiers = backend.get_node_edge_qualifiers(
                args['node'], lang=args['lang'], images=args['images'], fanouts=args['fanouts'], fmt=args['fmt'])
            return backend.query_result_to_string(qualifiers)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_inverse_edge_qualifiers'), methods=['GET'])
def get_node_inverse_edge_qualifiers():
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            qualifiers = backend.get_node_inverse_edge_qualifiers(
                args['node'], lang=args['lang'], images=args['images'], fanouts=args['fanouts'], fmt=args['fmt'])
            return backend.query_result_to_string(qualifiers)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_configuration'), methods=['GET'])
def get_configuration():
    """Show the currently loaded configuration values."""
    try:
        with get_backend(app) as backend:
            return backend.query_result_to_string(backend.api.config)
    except Exception as e:
        print('ERROR: ' + str(e))


### Top-level entry points:

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_all_node_data'), methods=['GET'])
def get_all_node_data():
    """Top-level method that collects all of a node's edge data,
    label strings dictionary, and whatever else we might need, and
    returns it all in a single 'kgtk_object_collection' JSON structure.
    """
    args = get_request_args()
    if args['node'] is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        with get_backend(app) as backend:
            data = backend.get_all_node_data(
                args['node'], lang=args['lang'], images=args['images'], fanouts=args['fanouts'], inverse=args['inverse'])
            return data or {}
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
