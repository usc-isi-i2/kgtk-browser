"""
Kypher backend support for the KGTK browser.
"""

import os.path
from http import HTTPStatus
import typing

import flask
import browser.backend.kypher as kybe

from kgtk.kgtkformat import KgtkFormat
from kgtk.value.kgtkvalue import KgtkValue


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


def build_current_value(backend,
                        node2: str,
                        value: KgtkValue,
                        rb_type: str,
                        node2_label: typing.Optional[str],
                        node2_description: typing.Optional[str],
                        units_node_cache: typing.MutableMapping[str, typing.Optional[str]],
                        lang: str,
                        )->typing.Mapping[str, str]:
    current_value: typing.MutableMapping[str, any] = dict()
    datatype: KgtkFormat.DataType = value.classify()
    if rb_type == "/w/item":
        current_value["ref"] = node2
        current_value["text"] = KgtkFormat.unstringify(node2_label) if node2_label is not None and len(node2_label) > 0 else ""
        current_value["description"] = KgtkFormat.unstringify(node2_description) if node2_description is not None and len(node2_description) > 0 else ""

    elif rb_type == "/w/text":
        text_value: str
        language: str
        language_suffix: str
        text_value, language, language_suffix = KgtkFormat.destringify(node2)
        current_value["text"] = text_value
        current_value["lang"] = language + language_suffix

    elif rb_type == "/w/string":
        current_value["text"] = KgtkFormat.unstringify(node2)

    elif rb_type == "/w/quantity":
        if datatype == KgtkFormat.DataType.NUMBER:
            current_value["text"] = node2
        else:
            if value.parse_fields():
                newnum: str = value.fields.numberstr
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
                    if units_node not in units_node_cache:
                        units_node_labels: typing.List[typing.List[str]] = backend.get_node_labels(units_node, lang=lang)
                        if len(units_node_labels) > 0:
                            units_node_label: str = units_node_labels[0][1]
                            units_node_cache[units_node] = KgtkFormat.unstringify(units_node_label)
                        else:
                            units_node_cache[units_node] = None # Remember the failure.
                                       
                    if units_node_cache[units_node] is not None:
                        newnum += " " + units_node_cache[units_node] + " (" + units_node + ")"
                    else:
                        newnum += " " + units_node # We could not find a label for this node when we looked last time.

                current_value["text"] = newnum
            else:
                # Validation failed.
                #
                # TODO: Add a validation failure indicator?
                current_value["text"] = node2

    elif rb_type == "/w/time":
        current_value["text"] = node2[1:] # Consider reformatting.
        
    elif rb_type == "/w/geo":
        current_value["text"] = node2[1:] # Consider reformatting
        # "url": "http://maps.google.com/maps?q=51.566513061523438,-0.14549720287322998"
    else:
        print("*** unknown rb_type %s" % repr(rb_type)) # ***

    return current_value

def find_rb_type(node2: str, value: KgtkValue)->str:
    datatype: KgtkFormat.DataType = value.classify()
    rb_type: str

    if datatype == KgtkFormat.DataType.SYMBOL:
        if node2.startswith(("P", "Q")):
            rb_type = "/w/item"
        else:
            rb_type = "unknown"
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

def rb_send_kb_item(item: str):
    lang: str = 'en'

    units_node_cache: typing.MutableMap[str, typing.Optional[str]] = dict()
    
    try:
        with get_backend(app) as backend:
            response: typing.MutableMapping[str, any] = dict()
            response["ref"] = item

            item_labels: typing.List[typing.List[str]] = backend.get_node_labels(item, lang=lang)
            response["text"] = KgtkFormat.unstringify(item_labels[0][1]) if len(item_labels) > 0 else item

            item_descriptions: typing.List[typing.List[str]] = backend.get_node_descriptions(item, lang=lang)
            response["description"] = KgtkFormat.unstringify(item_descriptions[0][1]) if len(item_descriptions) > 0 else item

            response_properties = [ ]
            response["properties"] = response_properties

            item_edges: typing.List[typing.List[str]] = backend.rb_get_node_edges(item, lang=lang)
            edge_id: str
            relationship: str
            node2: str
            relationship_label: typing.Optional[str]
            node2_label: typing.Optional[str]
            node2_description: typing.Optional[str]

            item_qualifier_edges: typing.List[typing.List[str]] = backend.rb_get_node_edge_qualifiers(item, lang=lang)

            qual_edge_id: str
            item_qual_map: typing.MutableMapping[str, typing.List[typing.List[str]]] = dict()
            item_qual_edge: typing.List[str]
            for item_qual_edge in item_qualifier_edges:
                edge_id = item_qual_edge[0]
                if edge_id not in item_qual_map:
                    item_qual_map[edge_id] = [ ]
                item_qual_map[edge_id].append(item_qual_edge)
                
            current_edge_id: typing.Optional[str] = None
            current_relationship: typing.Optional[str] = None
            current_property_map: typing.MutableMapping[str, any] = dict()
            current_values: typing.List[typing.MutableMapping[str, any]] = list()
            current_node2: typing.Optional[str] = None
            item_edge: typing.List[str]
            for item_edge in item_edges:
                print(repr(item_edge)) # ***
                edge_id, relationship, node2, relationship_label, node2_label, node2_description = item_edge

                if current_edge_id is not None and current_edge_id == edge_id:
                    print("*** skipping duplicate %s" % repr(current_edge_id)) # ***
                    # Skip duplicates (say, multiple labels or descriptions).
                    continue
                current_edge_id = edge_id

                value: KgtkValue = KgtkValue(node2)
                rb_type: str = find_rb_type(node2, value)
                
                if current_relationship is None or relationship != current_relationship:
                    current_relationship = relationship
                    current_property_map = dict()
                    response_properties.append(current_property_map)
                    current_property_map["ref"] = relationship
                    current_property_map["property"] = KgtkFormat.unstringify(relationship_label) if relationship_label is not None and len(relationship_label) > 0 else relationship
                    current_property_map["type"] = rb_type # TODO: check for consistency
                    current_values = list()
                    current_property_map["values"] = current_values

                current_value: typing.MutableMapping[str, any] = build_current_value(backend, node2, value, rb_type, node2_label, node2_description, units_node_cache, lang)
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
                        print(repr(item_qual_edge)) # ***
                        _, qual_edge_id, qual_relationship, qual_node2, qual_relationship_label, qual_node2_label, qual_node2_description = item_qual_edge
                        
                        if current_qual_edge_id is not None and current_qual_edge_id == qual_edge_id:
                            print("*** skipping duplicate qualifier %s" % repr(current_qual_edge_id)) # ***
                            # Skip duplicates (say, multiple labels or descriptions).
                            continue
                        current_qual_edge_id = qual_edge_id
                        
                        qual_value: KgtkValue = KgtkValue(qual_node2)
                        qual_rb_type: str = find_rb_type(qual_node2, qual_value)

                        if current_qual_relationship is None or qual_relationship != current_qual_relationship:
                            current_qual_relationship = qual_relationship
                            current_qual_property_map = dict()
                            current_qualifiers.append(current_qual_property_map)
                            current_qual_property_map["ref"] = qual_relationship
                            current_qual_property_map["property"] = KgtkFormat.unstringify(qual_relationship_label) if qual_relationship_label is not None and len(qual_relationship_label) > 0 else qual_relationship
                            current_qual_property_map["type"] = qual_rb_type # TODO: check for consistency
                            current_qual_values = list()
                            current_qual_property_map["values"] = current_qual_values
                    
                        current_qual_value: typing.MutableMapping[str, any] = build_current_value(backend,
                                                                                                  qual_node2,
                                                                                                  qual_value,
                                                                                                  qual_rb_type,
                                                                                                  qual_node2_label,
                                                                                                  qual_node2_description,
                                                                                                  units_node_cache,
                                                                                                  lang)
                        current_qual_values.append(current_qual_value)


            response["xrefs"] = [ ]

            response["categories"] = [ ]

            response["gallery"] = [ ]

            response["url"] = "https://sample.url"

            response["document"] = "Sample document: " + item

            return flask.jsonify(response), 200
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

@app.route('/kb/item', methods=['GET'])
def rb_get_kb_item():
    item = flask.request.args.get('id')
    print("rb_get_kb_item: " + item)
    return rb_send_kb_item(item)


@app.route('/kb/<string:item>', methods=['GET'])
def rb_get_kb_named_item(item):
    print("get_kb_named_item: " + item)
    if item.startswith("Q") or item.startswith("P"):
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
