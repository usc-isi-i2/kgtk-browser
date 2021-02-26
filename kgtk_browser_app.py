"""
Kypher backend support for the KGTK browser.
"""

import os.path
from http import HTTPStatus

import flask
import browser.backend.kypher as kybe


# How to run:
# > export FLASK_APP=kgtk_browser_app.py
# > export FLASK_ENV=development
# > export KGTK_BROWSER_CONFIG=$PWD/kgtk_browser_config.py
# > flask run

# Example invocation:
# http://127.0.0.1:5000/kgtk/browser/backend/get_all_node_data?node=Q5


### Flask application

app = flask.Flask(__name__)
app.config.from_envvar('KGTK_BROWSER_CONFIG')

DEFAULT_SERVICE_PREFIX = '/kgtk/browser/backend/'
app.config['SERVICE_PREFIX'] = app.config.get('SERVICE_PREFIX', DEFAULT_SERVICE_PREFIX)

app.kgtk_backend = kybe.BrowserBackend(app)


### Multi-threading
#
# These are just stubs for now, we need to figure out how to implement proper locking
# and how to cache thread-local instances of the sqlstore and its SQLite connection.

def acquire_backend(app):
    return app.kgtk_backend

def release_backend(app):
    pass


### URL handlers:
#
# These all call the corresponding backend method with the same name.
# Most of these are just test drivers, the top-level methods are the
# JSON-generating handlers at the end.

# Status codes: https://docs.python.org/3/library/http.html

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'test_get_edges'), methods=['GET'])
def test_get_edges():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    return 'get_edges %s ' % node

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edges'), methods=['GET'])
def get_node_edges():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        edges = backend.get_node_edges(node)
        return backend.query_result_to_list(edges)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_labels'), methods=['GET'])
def get_node_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        labels = backend.get_node_labels(node)
        return backend.query_result_to_list(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_aliases'), methods=['GET'])
def get_node_aliases():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        aliases = backend.get_node_aliases(node)
        return backend.query_result_to_list(aliases)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_descriptions'), methods=['GET'])
def get_node_descriptions():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        descriptions = backend.get_node_descriptions(node)
        return backend.query_result_to_list(descriptions)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_qualifiers'), methods=['GET'])
def get_node_edge_qualifiers():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        qualifiers = backend.get_node_edge_qualifiers(node)
        return backend.query_result_to_list(qualifiers)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)


@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_label_labels'), methods=['GET'])
def get_node_edge_label_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        labels = backend.get_node_edge_label_labels(node)
        return backend.query_result_to_list(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_node2_labels'), methods=['GET'])
def get_node_edge_node2_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        labels = backend.get_node_edge_node2_labels(node)
        return backend.query_result_to_list(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_qualifier_label_labels'), methods=['GET'])
def get_node_edge_qualifier_label_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        labels = backend.get_node_edge_qualifier_label_labels(node)
        return backend.query_result_to_list(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_edge_qualifier_node2_labels'), methods=['GET'])
def get_node_edge_qualifier_node2_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        labels = backend.get_node_edge_qualifier_node2_labels(node)
        return backend.query_result_to_list(labels)
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)


### Top-level entry points:

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_graph_data'), methods=['GET'])
def get_node_graph_data():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        data = backend.get_node_graph_data(node)
        return data
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_node_object_labels'), methods=['GET'])
def get_node_object_labels():
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        data = backend.get_node_object_labels(node)
        return data
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)

@app.route(os.path.join(app.config['SERVICE_PREFIX'], 'get_all_node_data'), methods=['GET'])
def get_all_node_data():
    """Top-level method that collects all of a node's edge data,
    label strings dictionary, and whatever else we might need, and
    returns it all in a single kgtk_object_collection JSON structure.
    """
    node = flask.request.args.get('node')
    if node is None:
        flask.abort(HTTPStatus.BAD_REQUEST.value)
    try:
        backend = acquire_backend(app)
        data = backend.get_all_node_data(node)
        return data
    except Exception as e:
        print('ERROR: ' + str(e))
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)
    finally:
        release_backend(app)
