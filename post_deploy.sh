#!/bin/bash
set -e

set echo

export INPUT_FILE="/data/kg_files/venice.tsv"
export GRAPH_CACHE="/data/database/venice.sqlite3.db"

# *********************************************************************
# *** Load the various types of edges into the graph cache. ***

# Remove any existing graph cache file:
echo "\nRemoving ${GRAPH_CACHE}"
rm -f ${GRAPH_CACHE}

# ********************************************************
#  Build the "node1;upper" column in the label table:
echo "\nbuilding node1;upper column"
time sqlite3 ${GRAPH_CACHE} 'ALTER TABLE graph_2 ADD COLUMN "node1;upper" text'

time sqlite3 ${GRAPH_CACHE} 'UPDATE graph_2 SET "node1;upper" = upper(node1)'

# Index the node1;upper column.  It supports case-insensitive
# searches on item labels.
echo "\nindexing node1;upper column"
time sqlite3 ${GRAPH_CACHE} 'CREATE INDEX "graph_2_node1upper_idx" on graph_2 ("node1;upper")'

time sqlite3 ${GRAPH_CACHE} 'ANALYZE "graph_2_node1upper_idx"'

#  Build the "node2;upper" column in the label table:
echo "\nbuilding node2;upper column"
time sqlite3 ${GRAPH_CACHE} 'ALTER TABLE graph_2 ADD COLUMN "node2;upper" text'

time sqlite3 ${GRAPH_CACHE} 'UPDATE graph_2 SET "node2;upper" = upper(node2)'

# Index the node2;upper column.  It supports case-insensitive
# searches on item labels.
echo "\nindexing node2;upper column"
time sqlite3 ${GRAPH_CACHE} 'CREATE INDEX "graph_2_node2upper_idx" on graph_2 ("node2;upper")'

time sqlite3 ${GRAPH_CACHE} 'ANALYZE "graph_2_node2upper_idx"'
