### KGTK browser configuration

import kgtk.kypher.api as kapi


### Basic configuration section:

GRAPH_CACHE           = '/data/rogers/Arnold_Schwarzenegger/cache/browser.sqlite3.db'
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
KG_DATATYPES_GRAPH     = 'metadata'

# edge labels for various edges referenced in query section below:
KG_LABELS_LABEL       = 'label'
KG_ALIASES_LABEL      = 'alias'
KG_DESCRIPTIONS_LABEL = 'description'
KG_IMAGES_LABEL       = 'P18'
KG_FANOUTS_LABEL      = 'count_distinct_properties'
KG_DATATYPES_LABEL     = 'datatype'

# configuration for display in the browser:
GRAPH_ID = "Tutorial"
VERSION = "20211011"


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
_api.add_input(KG_DATATYPES_GRAPH, name='datatypes', handle=True)

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

RB_UPPER_NODE_LABELS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_labels()'
    for case_independent searches.
    Given parameters 'NODE' and 'LANG' retrieve labels for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_label' pairs as the result (we include
    'NODE' as an output to make it easier to union result frames).
    """,
    name='rb_upper_node_labels_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n {upper: un})-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='un=$NODE and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'distinct n as node1, l as node_label',
)

RB_NODES_WITH_LABEL_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_with_label()'.
    Given parameters 'LABEL' and 'LANG' retrieve nodes with labels matching 'LABEL' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_label' pairs as the result

    For proper performace, 'node2' in the label graph must be indexed:

    CREATE INDEX "graph_2_node2_idx" ON graph_2 ("node2");
    ANALYZE "graph_2_node2_idx";
    """,
    name='rb_nodes_with_label_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='l=$LABEL and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'distinct n as node1, l as node_label',
)

RB_NODES_WITH_UPPER_LABEL_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_with_upper_label()'.
    Given parameters 'LABEL' and 'LANG' retrieve nodes with labels matching 'LABEL' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return distinct 'node1', 'node_label' pairs as the result

    This query implements a case-insensitive search by matching against the
    'node2;upper' column, which has the 'node2' column in the label graph
    ('graph_2') translated to upper case.  'node2;upper' may be created with
    `kgtk calc` or `kgtk query`, or with the following SQL:

    alter table graph_2 add column "node2;upper" text;
    update graph_2 set "node2;upper" = upper(node2);

    For proper performance, "node2;upper" must be indexed:

    CREATE INDEX "graph_2_node2upper_idx" ON graph_2 ("node2;upper");
    ANALYZE "graph_2_node2upper_idx";
    """,
    name='rb_nodes_with_upper_label_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l {upper: ul})' % KG_LABELS_LABEL,
    where='ul=$LABEL and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'distinct n as node1, l as node_label',
)

RB_NODES_STARTING_WITH_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_starting_with()'.
    Given parameters 'NODE' (which should end with '*') and 'LANG' retrieve labels for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return 'node1', 'node_label' pairs as the result.
    Limit the number of return pairs to LIMIT.
    """,
    name='rb_nodes_starting_with_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='glob($NODE, n) and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'n as node1, l as node_label',
    order= "n, l", # Questionable performance due to poor interaction with limit
    limit= "$LIMIT"
)

RB_UPPER_NODES_STARTING_WITH_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_starting_with()' for case-insensitive searches.
    Given parameters 'NODE' (which should end with '*') and 'LANG' retrieve labels for 'NODE' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return 'node1', 'node_label' pairs as the result.
    Limit the number of return pairs to LIMIT.
    """,
    name='rb_upper_nodes_starting_with_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n {upper: un})-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='glob($NODE, un) and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'n as node1, l as node_label',
    order= "n, l", # Questionable performance due to poor interaction with limit
    limit= "$LIMIT"
)

RB_NODES_WITH_LABELS_STARTING_WITH_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_with_labels_starting_with()'.
    Given parameters 'LABEL' (which should end with '*') and 'LANG' retrieve labels for 'LABEL' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return 'node1', 'node_label' pairs as the result.
    Limit the number of return pairs to LIMIT.

    The output from this query is unordered, due to poor perfromance when
    there are a large number of matches.

    For proper performace, the 'node2' column in the label graph must be indexed:

    CREATE INDEX "graph_2_node2_idx" ON graph_2 ("node2");
    ANALYZE "graph_2_node2_idx";
    """,
    name='rb_nodes_with_labels_starting_with_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l)' % KG_LABELS_LABEL,
    where='glob($LABEL, l) and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'n as node1, l as node_label',
    # order= "n, l", # This kills performance when there is a large number of matches
    limit= "$LIMIT"
)

RB_NODES_WITH_UPPER_LABELS_STARTING_WITH_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_nodes_with_labels_starting_with()'.
    Given parameters 'LABEL' (which should end with '.*') and 'LANG' retrieve labels for 'LABEL' in
    the specified language (using 'any' for 'LANG' retrieves all labels).
    Return 'node1', 'node_label' pairs as the result.
    Limit the number of return pairs to LIMIT.

    The output from this query is unordered, due to poor perfromance when
    there are a large number of matches.

    This query implements a case-insensitive search by matching against the
    'node2;upper' column, which has the 'node' column in the label graph
    ('graph_2') translated to upper case.  'node2;upper' may be created with
    `kgtk calc` or `kgtk query`, or with the following SQL:

    alter table graph_2 add column "node2;upper" text;
    update graph_2 set "node2;upper" = upper(node2);

    For proper performance, the "node2;upper" column in the label graph must be indexed:

    CREATE INDEX "graph_2_node2upper_idx" ON graph_2 ("node2;upper");
    ANALYZE "graph_2_node2upper_idx";
    """,
    name='rb_nodes_with_upper_labels_starting_with_query',
    inputs='labels',
    maxcache=MAX_CACHE_SIZE * 10,
    match='$labels: (n)-[r:`%s`]->(l {upper: ul})' % KG_LABELS_LABEL,
    where='glob($LABEL, ul) and ($LANG="any" or kgtk_lqstring_lang(l)=$LANG)',
    ret=  'n as node1, l as node_label',
    # order= "n, l", # This kills performance when there is a large number of matches
    limit= "$LIMIT"
)

RB_NODE_EDGES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_node_edges()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node1.
    Additionally retrieve descriptive information for all relationship labels.
    Additionally retrieve the node2 descriptions.
    Parameter 'LANG' controls the language for retrieved labels.
    Return edge 'id', 'label', 'node2', as well as node2's 'node2_label'
    and label's 'label_label'.

    """,
    name='rb_node_edges_query',
    inputs=('edges', 'labels', 'descriptions', 'datatypes'),
    match= '$edges: (n1)-[r {label: rl}]->(n2)',
    where= 'n1=$NODE',
    opt=   '$labels: (rl)-[:`%s`]->(llabel)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(llabel)=$LANG',
    opt2=   '$labels: (n2)-[:`%s`]->(n2label)' % KG_LABELS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(n2label)=$LANG',
    opt3=   '$descriptions: (n2)-[r:`%s`]->(n2desc)' % KG_DESCRIPTIONS_LABEL,
    owhere3='$LANG="any" or kgtk_lqstring_lang(n2desc)=$LANG',
    opt4=   '$datatypes: (rl)-[:`%s`]->(rlwdt)' % KG_DATATYPES_LABEL,
    ret=   'r as id, ' +
           'n1 as node1, ' +
           'r.label as relationship, ' +
           'n2 as node2, ' +
           'llabel as relationship_label, ' +
           'n2 as target_node, ' +
           'n2label as target_label, ' +
           'n2desc as target_description, ' +
           'rlwdt as wikidatatype',
    order= 'r.label, n2, r, llabel, n2label, n2desc',
    limit= "$LIMIT"
)

RB_NODE_EDGE_QUALIFIERS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_edge_qualifiers()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node1
    and then all qualifier edges for all such base edges found.  For each 
    qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
    for base edges.
    """,
    name='rb_node_edge_qualifiers_query',
    inputs=('edges', 'qualifiers', 'labels', 'descriptions'),
    match= '$edges: (n1)-[r]->(n2), $qualifiers: (r)-[q {label: ql}]->(qn2)',
    where= 'n1=$NODE',
    opt=   '$labels: (ql)-[:`%s`]->(qllabel)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(qllabel)=$LANG',
    opt2=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
    opt3=   '$descriptions: (qn2)-[r:`%s`]->(qd)' % KG_DESCRIPTIONS_LABEL,
    owhere3='$LANG="any" or kgtk_lqstring_lang(qd)=$LANG',
    ret=   'r as id, ' +
           'n1 as node1, ' +
           'q as qual_id, ' +
           'q.label as qual_relationship, ' +
           'qn2 as qual_node2, ' +
           'qllabel as qual_relationship_label, ' +
           'qn2label as qual_node2_label, ' +
           'qd as qual_node2_description',
    order= 'r, q.label, qn2, q, qllabel, qn2label, qd',
    limit= "$LIMIT"
)

RB_NODE_EDGE_QUALIFIERS_BY_EDGE_ID_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_edge_qualifiers()'.
    Given parameter 'NODE' retrieve all edges that have 'EDGE_ID' as their edge ID
    and then all qualifier edges for all such base edges found.  For each 
    qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
    for base edges.
    """,
    name='rb_node_edge_qualifiers_by_edge_id_query',
    inputs=('edges', 'qualifiers', 'labels', 'descriptions'),
    match= '$edges: (n1)-[r]->(n2), $qualifiers: (r)-[q {label: ql}]->(qn2)',
    where= 'r=$EDGE_ID',
    opt=   '$labels: (ql)-[:`%s`]->(qllabel)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(qllabel)=$LANG',
    opt2=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
    opt3=   '$descriptions: (qn2)-[r:`%s`]->(qd)' % KG_DESCRIPTIONS_LABEL,
    owhere3='$LANG="any" or kgtk_lqstring_lang(qd)=$LANG',
    ret=   'r as id, ' +
           'n1 as node1, ' +
           'q as qual_id, ' +
           'q.label as qual_relationship, ' +
           'qn2 as qual_node2, ' +
           'qllabel as qual_relationship_label, ' +
           'qn2label as qual_node2_label, ' +
           'qd as qual_node2_description',
    order= 'r, q.label, qn2, q, qllabel, qn2label, qd', # For better performance with LIMIT, sort in caller.
    limit="$LIMIT"
)

def GET_RB_NODE_EDGE_QUALIFIERS_IN_QUERY(id_list):
    """This code generates a new name for each query, thus
    rendering the query cache ineffective and filled with junk.

    The conversion applied to `id_list` does not take into
    consideration that Python and SQL are lilely to have
    different approaches to strings with embedded quotes.
    Fortunately, we do not expect embedded quotes in the
    id_list.

    Do not supply a name for these queries.
    """
    return _api.get_query(
        doc="""
        Create the Kypher query used by 'BrowserBackend.get_node_edge_qualifiers_in()'.
        Given parameter 'ID_LIST' retrieve all edges that have their ID in 'ID_LIST'
        and then all qualifier edges for all such base edges found.  For each 
        qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
        for base edges.
        """,
        inputs=('edges', 'qualifiers', 'labels', 'descriptions'),
        match= '$edges: (n1)-[r]->(n2), $qualifiers: (r)-[q {label: ql}]->(qn2)',
        where= 'r in [' + ", ".join([repr(id_value) for id_value in id_list]) + ']',
        opt=   '$labels: (ql)-[:`%s`]->(qllabel)' % KG_LABELS_LABEL,
        owhere='$LANG="any" or kgtk_lqstring_lang(qllabel)=$LANG',
        opt2=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
        owhere2='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
        opt3=   '$descriptions: (qn2)-[r:`%s`]->(qd)' % KG_DESCRIPTIONS_LABEL,
        owhere3='$LANG="any" or kgtk_lqstring_lang(qd)=$LANG',
        ret=   'r as id, ' +
        'n1 as node1, ' +
        'q as qual_id, ' +
        'q.label as qual_relationship, ' +
        'qn2 as qual_node2, ' +
        'qllabel as qual_relationship_label, ' +
        'qn2label as qual_node2_label, ' +
        'qd as qual_node2_description',
        order= 'r, q.label, qn2, q, qllabel, qn2label, qd',
        limit= "$LIMIT"
    )

RB_NODE_INVERSE_EDGES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_node_inverse_edges()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node2.
    Additionally retrieve descriptive information for all relationship labels.
    Additionally retrieve descriptive information for all node2's such as their
    label, and optionally any images and fanouts.  Parameter 'LANG' controls
    the language for retrieved labels.
    Return edge 'id', 'label', 'node2', as well as node2's 'node2_label'
    and label's 'label_label'.

    """,
    name='rb_node_inverse_edges_query',
    inputs=('edges', 'labels', 'descriptions', 'datatypes'),
    match= '$edges: (n1)-[r {label: rl}]->(n2)',
    where= 'n2=$NODE',
    opt=   '$labels: (rl)-[:`%s`]->(llabel)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(llabel)=$LANG',
    opt2=   '$labels: (n1)-[:`%s`]->(n1label)' % KG_LABELS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(n1label)=$LANG',
    opt3=   '$descriptions: (n1)-[r:`%s`]->(n1desc)' % KG_DESCRIPTIONS_LABEL,
    owhere3='$LANG="any" or kgtk_lqstring_lang(n1desc)=$LANG',
    opt4=   '$datatypes: (rl)-[:`%s`]->(rlwdt)' % KG_DATATYPES_LABEL,
    ret=   'r as id, ' +
           'n1 as node1, ' +
           'r.label as relationship, ' +
           'n2 as node2, ' +
           'llabel as relationship_label, ' +
           'n1 as target_node, ' +
           'n1label as target_label, ' +
           'n1desc as target_description, ' +
           'rlwdt as wikidatatype',
    order= 'r.label, n2, r, llabel, n1label, n1desc'
)

RB_NODE_INVERSE_EDGE_QUALIFIERS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.get_node_inverse_edge_qualifiers()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node2
    and then all qualifier edges for all such base edges found.  For each 
    qualifier edge return information similar to what 'NODE_EDGES_QUERY' returns
    for base edges.
    """,
    name='rb_node_inverse_edge_qualifiers_query',
    inputs=('edges', 'qualifiers', 'labels', 'descriptions'),
    match= '$edges: (n1)-[r]->(n2), $qualifiers: (r)-[q {label: ql}]->(qn2)',
    where= 'n2=$NODE',
    opt=   '$labels: (ql)-[:`%s`]->(qllabel)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(qllabel)=$LANG',
    opt2=   '$labels: (qn2)-[:`%s`]->(qn2label)' % KG_LABELS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(qn2label)=$LANG',
    opt3=   '$descriptions: (qn2)-[r:`%s`]->(qd)' % KG_DESCRIPTIONS_LABEL,
    owhere3='$LANG="any" or kgtk_lqstring_lang(qd)=$LANG',
    ret=   'r as id, ' +
           'n1 as node1, ' +
           'q as qual_id, ' +
           'q.label as qual_relationship, ' +
           'qn2 as qual_node2, ' +
           'qllabel as qual_relationship_label, ' +
           'qn2label as qual_node2_label, ' +
           'qd as qual_node2_description',
    order= 'r, q.label, qn2, q, qllabel, qn2label, qd'
)

RB_NODE_CATEGORIES_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_node_categories()'.
    Given parameter 'NODE' retrieve all edges that have 'NODE' as their node2
    under relationship P301.
    Additionally retrieve descriptive information for all relationship labels.
    Additionally retrieve descriptive information for all node2's such as their
    label, and optionally any images and fanouts.  Parameter 'LANG' controls
    the language for retrieved labels.
    Return the category `node1`, 'node1_label', and'node1_description'.

    WARNING! This query may be incorrect, and should be considered a placeholder.

    """,
    name='rb_node_categories_query',
    inputs=('edges', 'labels', 'descriptions'),
    match= '$edges: (n1)-[:P301]->(n2)',
    where= 'n2=$NODE',
    opt=   '$labels: (n1)-[:`%s`]->(n1label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(n1label)=$LANG',
    opt2=   '$descriptions: (n1)-[r:`%s`]->(n1desc)' % KG_DESCRIPTIONS_LABEL,
    owhere2='$LANG="any" or kgtk_lqstring_lang(n1desc)=$LANG',
    ret=   'n1 as node1, ' +
           'n1label as node1_label, ' +
           'n1desc as node1_description',
    order= 'n1, n1label, n1desc'
)


RB_IMAGE_FORMATTER_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_image_formatter()'.
    Given parameter 'NODE' retrieve the first edge's node2 value that has 'NODE' as the node1
    under relationship P1630.
    Return node2.
    """,
    name='rb_image_formatter_query',
    inputs=('edges'),
    match= '$edges: (n1)-[:P1630]->(n2)',
    where= 'n1=$NODE',
    ret=   'n2 as node2 ',
    limit= 1
)

RB_SUBPROPERTY_RELATIONSHIPS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_subproperty_relationships()'.
    Return node1 and node2.
    """,
    name='rb_subproperty_relationships_query',
    inputs=('edges', 'labels'),
    match= '$edges: (n1)-[:P1647]->(n2)',
    opt=   '$labels: (n1)-[:`%s`]->(n1label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(n1label)=$LANG',
    ret=   'n1 as node1, n2 as node2, n1label as node1_label',
)

RB_LANGUAGE_LABELS_QUERY = _api.get_query(
    doc="""
    Create the Kypher query used by 'BrowserBackend.rb_get_language_labels()'.
    Given parameter 'CODE' retrieve all edges that have 'CODE' as their node2
    under relationship P424, validated by P31->Q34770 (instance_of language).

    The validation is needed because P424 (Wikimedia language code) also
    appears in in other contexts (e.g., Q15156406 (English Wikisource)).

    However, some languages (Esperanto (Q143) and Armenian (Q8785), for
    example) are not marked as instance of (P31) language (Q34770).

    So, we accept instance of modern language (Q1288568) or natural
    language (Q33742) as alternatives.

    Alternative approaches include:
    1) Excluding the items we don't want. e.g. exclude items that
       are instances of (P31) Wikisource language edition (Q15156455).
    2) Looking for entries with aliases equal to the language code.
    3) Looking for entries with matching Identifiers.
    4) Encouraging Wikidata to consistently mark languages.    
    
    Returns the labels for the node1's.
    Parameter 'LANG' controls the language for retrieved labels.
    Return the category `node1` and 'node1_label'.
    """,
    name='rb_language_labels_query',
    inputs=('edges', 'labels'),
    match= '$edges: (isa)<-[:P31]-(n1)-[:P424]->(n2)',
    where= 'n2=$CODE and isa in ["Q34770", "Q1288568", "Q33742"]',
    opt=   '$labels: (n1)-[:`%s`]->(n1label)' % KG_LABELS_LABEL,
    owhere='$LANG="any" or kgtk_lqstring_lang(n1label)=$LANG',
    ret=   'n1 as node1, n1label as node1_label',
    order= 'n1, n1label'
)
