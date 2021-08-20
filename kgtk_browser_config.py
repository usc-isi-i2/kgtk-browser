### KGTK browser configuration

import kgtk.kypher.api as kapi


### Basic configuration section:

GRAPH_CACHE           = './wikidata.sqlite3.db'
LOG_LEVEL             = 1
INDEX_MODE            = 'auto'
MAX_RESULTS           = 10000
MAX_CACHE_SIZE        = 1000
#DEFAULT_FANOUT        = 10       # not yet implemented
DEFAULT_LANGUAGE      = 'en'

# input names for various aspects of the KG referenced in query section below:
KG_EDGES_GRAPH        = 'claims'
KG_QUALIFIERS_GRAPH   = 'qualifiers'
KG_LABELS_GRAPH       = 'labels'
KG_ALIASES_GRAPH      = 'aliases'
KG_DESCRIPTIONS_GRAPH = 'descriptions'
KG_IMAGES_GRAPH       = 'claims'
KG_FANOUTS_GRAPH      = 'metadata'

# edge labels for various edges referenced in query section below:
KG_LABELS_LABEL       = 'label'
KG_ALIASES_LABEL      = 'alias'
KG_DESCRIPTIONS_LABEL = 'description'
KG_IMAGES_LABEL       = 'P18'
KG_FANOUTS_LABEL      = 'count_distinct_properties'


### Query configuration section:

# The queries defined below are used by the backend to retrieve and
# aggregate information about nodes.  It should generally not be
# necessary to adapt these queries unless the schema of the knowledge
# graph significantly deviates from the standard KGTK schema used for
# Wikidata.  By 'schema' we mean what kind of labels are used for
# edges and what kind of representation scheme is used for certain
# information.  For example, an edge label description string might be
# attached as a 'label' edge from the edge label (such as 'P31'), or
# it might be attached, for example, via some intermediate node.
# Similarly, queries might access information from an actual graph
# table, or instead return dummy default values (e.g., to return the
# same default fanout for every edge), or compute a value in some way.

# The backend makes assumptions about the columns retrieved by each
# query and what kind of parameters each of them take.  If a query
# gets modified, these assumption need to be met to not require any
# backend reprogramming.  If data relevant to a particular parameter
# is not available (e.g., a dataset might be monolingual or might not
# have any image information), parameters controlling that information
# may simply be ignored.  The doc string of each query describes its
# behavior in more detail.

_api = kapi.KypherApi(graphcache=GRAPH_CACHE, loglevel=LOG_LEVEL, index=INDEX_MODE,
                      maxresults=MAX_RESULTS, maxcache=MAX_CACHE_SIZE)

_api.add_input(KG_EDGES_GRAPH, name='edges', handle=True)
_api.add_input(KG_QUALIFIERS_GRAPH, name='qualifiers', handle=True)
_api.add_input(KG_LABELS_GRAPH, name='labels', handle=True)
_api.add_input(KG_ALIASES_GRAPH, name='aliases', handle=True)
_api.add_input(KG_DESCRIPTIONS_GRAPH, name='descriptions', handle=True)
_api.add_input(KG_IMAGES_GRAPH, name='images', handle=True)
_api.add_input(KG_FANOUTS_GRAPH, name='fanouts', handle=True)

NODE_LABELS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_labels()'.
    Given parameters 'NODE' and 'LANG' retrieve labels for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_label' pairs as the result (we include
    'NODE' as an output to make it easier to union result frames).
    """,
    name='node_labels_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='n=$NODE and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'distinct n as node1, l as node_label',
)

NODE_ALIASES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_aliases()'.
    Given parameters 'NODE' and 'LANG' retrieve aliases for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_alias' pairs as the result.
    """,
    name='node_aliases_query',
    inputs='aliases',
    match='$aliases: (n)-[r:`%s`]->(a)' % KG_ALIASES_LABEL,
    where='n=$NODE and ($LANG="any" or kgtk_lqstring_lang(a)=$LANG)',
    ret=  'distinct n as node1, a as node_alias',
)

NODE_DESCRIPTIONS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_descriptions()'.
    Given parameters 'NODE' and 'LANG' retrieve descriptions for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_description' pairs as the result.
    """,
    name='node_descriptions_query',
    inputs='descriptions',
    match='$descriptions: (n)-[r:`%s`]->(d)' % KG_DESCRIPTIONS_LABEL,
    where='n=$NODE and ($LANG="any" or kgtk_lqstring_lang(d)=$LANG)',
    ret=  'distinct n as node1, d as node_description',
)

NODE_IMAGES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_images()'.
    Given parameter 'NODE' retrieve image URIs for 'NODE'.
    Return distinct 'node1', 'node_image' pairs as the result.
    """,
    name='node_images_query',
    inputs='images',
    match='$images: (n)-[r:`%s`]->(i)' % KG_IMAGES_LABEL,
    where='n=$NODE',
    ret=  'distinct n as node1, i as node_image',
)

NODE_EDGES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_edges()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node1.
    Additionally retrieve descriptive information for all node2's such as their
    label, and optionally any images and fanouts.  Parameter 'LANG' controls
    the language for retrieved labels, parameters 'FETCH_IMAGES' and 'FETCH_FANOUTS'
    control whether any images or fanouts should be returned.  If they are False,
    the corresponding result column values will all be None.
    Return edge 'id', 'node1', 'label', 'node2', as well as node2's 'node_label',
    and optional 'node_image' and 'node_fanout' as the result (note that in case
    of multiple node2 labels or images, edge row information may be duplicated).
    """,
    name='node_edges_query',
    inputs=('edges', 'labels', 'images', 'fanouts'),
    match= '$edges: (n1)-[r]->(n2)',
    where= 'n1=$NODE',
    opt=   '$labels: (n2)-[:`%s`]->(n2label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(n2label)=$LANG',
    opt2=  '$images: (n2)-[:`%s`]->(n2image)' % KG_IMAGES_LABEL,
    owhere2='$FETCH_IMAGES',
    opt3=  '$fanouts: (n2)-[:`%s`]->(n2fanout)' % KG_FANOUTS_LABEL,
    owhere3='$FETCH_FANOUTS',
    ret=   'r as id, n1 as node1, r.label as label, n2 as node2, ' +
           'n2label as node_label, n2image as node_image, n2fanout as node_fanout',
)

NODE_INVERSE_EDGES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_inverse_edges()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node2.
    Otherwise this is similar to 'NODE_EDGES_QUERY', just with descriptive
    information retrieved about edge node1's instead.
    """,
    name='node_inverse_edges_query',
    inputs=('edges', 'labels', 'images', 'fanouts'),
    match= '$edges: (n1)-[r]->(n2)',
    where= 'n2=$NODE',
    opt=   '$labels: (n1)-[:`%s`]->(n1label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(n1label)=$LANG',
    opt2=  '$images: (n1)-[:`%s`]->(n1image)' % KG_IMAGES_LABEL,
    owhere2='$FETCH_IMAGES',
    opt3=  '$fanouts: (n1)-[:`%s`]->(n1fanout)' % KG_FANOUTS_LABEL,
    owhere3='$FETCH_FANOUTS',
    ret=   'r as id, n1 as node1, r.label as label, n2 as node2, ' +
           'n1label as node_label, n1image as node_image, n1fanout as node_fanout',
)

NODE_EDGE_QUALIFIERS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_edge_qualifiers()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node1
    and then all qualifier edges for all such base edges found.  For each 
    qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
    for base edges.
    """,
    name='node_edge_qualifiers_query',
    inputs=('edges', 'qualifiers', 'labels', 'images', 'fanouts'),
    match= '$edges: (n1)-[r]->(), $qualifiers: (r)-[q]->(qn2)',
    where= 'n1=$NODE',
    opt=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
    opt2=  '$images: (qn2)-[:`%s`]->(qn2image)' % KG_IMAGES_LABEL,
    owhere2='$FETCH_IMAGES',
    opt3=  '$fanouts: (qn2)-[:`%s`]->(qn2fanout)' % KG_FANOUTS_LABEL,
    owhere3='$FETCH_FANOUTS',
    ret=   'q, r as node1, q.label as label, qn2 as node2, '+
           'qn2label as node_label, qn2image as node_image, qn2fanout as node_fanout',
    order= 'r, qn2 desc',
)

NODE_INVERSE_EDGE_QUALIFIERS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_inverse_edge_qualifiers()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node2
    and then all qualifier edges for all such inverse base edges found.  For each 
    qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
    for base edges.
    """,
    name='node_inverse_edge_qualifiers_query',
    inputs=('edges', 'qualifiers', 'labels', 'images', 'fanouts'),
    match= '$edges: ()-[r]->(n2), $qualifiers: (r)-[q]->(qn2)',
    where= 'n2=$NODE',
    opt=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
    opt2=  '$images: (qn2)-[:`%s`]->(qn2image)' % KG_IMAGES_LABEL,
    owhere2='$FETCH_IMAGES',
    opt3=  '$fanouts: (qn2)-[:`%s`]->(qn2fanout)' % KG_FANOUTS_LABEL,
    owhere3='$FETCH_FANOUTS',
    ret=   'q, r as node1, q.label as label, qn2 as node2, '+
           'qn2label as node_label, qn2image as node_image, qn2fanout as node_fanout',
    order= 'r, qn2 desc',
)
