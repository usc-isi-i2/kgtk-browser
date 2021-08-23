"""
Kypher backend support for the KGTK browser.
"""

import os.path
from http import HTTPStatus

import flask
import browser.backend.kypher as kybe
from kgtk.kgtkformat import KgtkFormat


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
def get_kb():
    return flask.send_from_directory('web/static', 'kb.html')

@app.route('/kb/query', methods=['GET'])
def get_kb_query():
    q = flask.request.args.get('q')
    print("get_kb_query: " + q)

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

def send_kb_item(item: str):
    response_data = {
        "ref": item,
        "text": "Sample text: " + item,
        "description": "Sample description: " + item,
        "properties": [ ],
        "xrefs": [ ],
        "categories": [ ],
        "gallery": [ ],
        "url": "https://sample.url",
        "document": "Sample document: " + item
    }
    
    return flask.jsonify(response_data), 200

@app.route('/kb/item', methods=['GET'])
def get_kb_item():
    item = flask.request.args.get('id')
    print("get_kb_item: " + item)
    return send_kb_item(item)


@app.route('/kb/<string:item>', methods=['GET'])
def get_kb_named_item(item):
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
