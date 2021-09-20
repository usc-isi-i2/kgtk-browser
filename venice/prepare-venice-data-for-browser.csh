#! /bin/tcsh

set echo

setenv INPUT_FILE "venice/venice_kgtk_file.tsv"
setenv GRAPH_CACHE "venice/venice.sqlite3.db"

# *********************************************************************
# *** Load the various types of edges into the graph cache. ***

# Remove any existing graph cache file:
echo "\nRemoving ${GRAPH_CACHE}"
rm -f ${GRAPH_CACHE}

# *********************************************************************
# *** Load everything into graph_1. ***
echo "\nLoad and index graph_1."
time kgtk query \
     -i ${INPUT_FILE} \
     --graph-cache ${GRAPH_CACHE} \
     --as claims --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_1_node1_idx" ON graph_1 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_node1_idx"'

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_1_label_idx" on graph_1 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_label_idx"'

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_1_node2_idx" on graph_1 ("node2")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_node2_idx"'

# The claims should have unique ID values.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE UNIQUE INDEX "graph_1_id_idx" on graph_1 ("id")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_id_idx"'

# ********************************************************
#  Build the "node1;upper" column for item name initial prefix searches:
time sqlite3 ${GRAPH_CACHE} \
     'ALTER TABLE graph_1 ADD COLUMN "node1;upper" text'

time sqlite3 ${GRAPH_CACHE} \
    'UPDATE graph_1 SET "node1;upper" = upper(node1) where label = '"'label'"

# Index the node1;upper column.  It supports case-insensitive
# prefix searches on item name.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_1_node1upper_idx" on graph_1 ("node1;upper")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_node1upper_idx"'

# *********************************************************************
#  Build the "node2;upper" column for label initial prefix searches:
time sqlite3 ${GRAPH_CACHE} \
     'ALTER TABLE graph_1 ADD COLUMN "node2;upper" text'

time sqlite3 ${GRAPH_CACHE} \
    'UPDATE graph_1 SET "node2;upper" = upper(node2) where label = '"'label'"

# Index the node2;upper column.  It supports case-insensitive
# prefix searches on item labels.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_1_node2upper_idx" on graph_1 ("node2;upper")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_1_node2upper_idx"'

# ********************************************************
# *** Verify that the graph cache has loaded as expected. ***
echo "\nVerify that the graph cache has loaded as expected."
time kgtk query --show-cache \
     --graph-cache ${GRAPH_CACHE}

time sqlite3 ${GRAPH_CACHE} <<EOF
.schema
EOF
