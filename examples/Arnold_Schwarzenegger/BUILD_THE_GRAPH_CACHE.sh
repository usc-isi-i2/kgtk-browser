#! /bin/bash

# Define some locations and options:
export GRAPHS="./graphs"
export GRAPH_CACHE="./cache/browser.sqlite3.db"

# There's no point in using "--progress", as it doesn't yet work
# properly with "kgtk query" and this project's data is processed very
# quickly.
export KGTK_OPTIONS=""

# ******************************************************************
# Remove any existing graph cache file:
echo -e "\n*** Removing ${GRAPH_CACHE} ***"
rm -f ${GRAPH_CACHE}

# ******************************************************************
# Load the various types of edges into the graph cache.  These loads
# must take place in the order shown.  If the loads are not completed
# in this order, then the sqlite3 commands that follow may execute on
# the wrong data.

# *** Load and index graph_1: claims. ***
echo -e "\n*** Load and index graph_1: claims. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/claims.tsv.gz \
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

# *** Load and index graph_2: labels. ***
echo -e "\n*** Load and index graph_2: labels. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/labels.tsv.gz \
     --graph-cache ${GRAPH_CACHE} \
     --as labels --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_2_node1_idx" on graph_2 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_2_node1_idx"'

# This index should not be needed, as there should be only one label
# value in the labels table:
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_2_label_idx" on graph_2 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_2_label_idx"'

# Index node2 for this graph! 
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_2_node2_idx" on graph_2 ("node2")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_2_node2_idx"'

# *** Load graph_3: aliases. ***
echo -e "\n*** Load graph_3: aliases. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/aliases.tsv.gz \
     --graph-cache ${GRAPH_CACHE} \
     --as aliases --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_3_node1_idx" on graph_3 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_3_node1_idx"'

# This index should not be needed, as there should be only one label
#  value in the aliases table:
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_3_label_idx" on graph_3 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_3_label_idx"'

# *** Load graph_4: descriptions. ***
echo -e "\n*** Load graph_4: descriptions. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/descriptions.tsv.gz \
     --graph-cache ${GRAPH_CACHE} \
     --as descriptions --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_4_node1_idx" on graph_4 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_4_node1_idx"'

# This index should not be needed, as there should be only one label
# value in the descriptions table:
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_4_label_idx" on graph_4 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_4_label_idx"'

# The descriptions should have unique ID values. ???
time sqlite3 ${GRAPH_CACHE} \
    'CREATE UNIQUE INDEX "graph_4_id_idx" on graph_4 ("id")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_4_id_idx"'

# *** Load graph_5: qualifiers. ***
echo -e "\n*** Load graph_5: qualifiers. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/quals.tsv.gz \
     --graph-cache ${GRAPH_CACHE} \
     --as qualifiers --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_5_node1_idx" on graph_5 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_5_node1_idx"'

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_5_label_idx" on graph_5 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_5_label_idx"'
 
# Index node2!
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_5_node2_idx" on graph_5 ("node2")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_5_node2_idx"'

# *** Load graph_6: metadata. ***
echo -e "\n*** Load graph_6: metadata. ***"
time kgtk ${KGTK_OPTIONS} query \
     -i ${GRAPHS}/metadata.tsv.gz \
     --graph-cache ${GRAPH_CACHE} \
     --as metadata --limit 1

time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_6_node1_idx" on graph_6 ("node1")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_6_node1_idx"'

# This index is needed only if metedata includes records
# other than datatype.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_6_label_idx" on graph_6 ("label")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_6_label_idx"'

# ********************************************************
#  Build the "node1;upper" column in the label table:
time sqlite3 ${GRAPH_CACHE} \
     'ALTER TABLE graph_2 ADD COLUMN "node1;upper" text'

time sqlite3 ${GRAPH_CACHE} \
    'UPDATE graph_2 SET "node1;upper" = upper(node1)'

# Index the node1;upper column.  It supports case-insensitive
# searches on item labels.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_2_node1upper_idx" on graph_2 ("node1;upper")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_2_node1upper_idx"'

#  Build the "node2;upper" column in the label table:
time sqlite3 ${GRAPH_CACHE} \
     'ALTER TABLE graph_2 ADD COLUMN "node2;upper" text'

time sqlite3 ${GRAPH_CACHE} \
    'UPDATE graph_2 SET "node2;upper" = upper(node2)'

# Index the node2;upper column.  It supports case-insensitive
# searches on item labels.
time sqlite3 ${GRAPH_CACHE} \
    'CREATE INDEX "graph_2_node2upper_idx" on graph_2 ("node2;upper")'

time sqlite3 ${GRAPH_CACHE} \
    'ANALYZE "graph_2_node2upper_idx"'

# ********************************************************
# Verify that the graph cache has loaded as expected.
echo -e "\n*** Verify that the graph cache has loaded as expected. ***"
time kgtk ${KGTK_OPTIONS} query --show-cache \
     --graph-cache ${GRAPH_CACHE}

time sqlite3 ${GRAPH_CACHE}<<EOF
.schema
EOF
