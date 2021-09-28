#! /bin/bash

# Define some locations and options:

INPUT_FILE="./data/Q2685.graph.all.tsv.gz"
export INPUT_FILE

WORKING_FOLDER="./temp"
export WORKING_FOLDER

FINAL_PRODUCTS="./data"
export FINAL_PRODUCTS

KGTK_OPTIONS="--progress"
export KGTK_OPTIONS

MGZIP_OPTIONS="--use-mgzip --mgzip-threads=5"
export MGZIP_OPTIONS

# If pigz is installed, you can enable it for better sorting performance.
GZIP_CMD="--gzip-command=pigz"
# GZIP_CMD=""
export GZIP_CMD

# Sort options
SORT_PARALLEL=20
export SORT_PARALLEL

SORT_BUFFER_SIZE="25%"
export SORT_BUFFER_SIZE

TEMP_FOLDER="./data/temp"
export TEMP_FOLDER

# Create the working folder and final products folder:
mkdir -p ${WORKING_FOLDER}
mkdir -p ${FINAL_PRODUCTS}

# ******************************************************************
# Split the unified input file into:
#    aliases
#    descriptions
#    labels
#    metadata (datatypes)
#    claims and qualifiers
#
# Also split out "link" records, they shouldn't be there.
time kgtk ${KGTK_OPTIONS} filter ${MGZIP_OPTIONS} \
     -i ${INPUT_FILE} \
     -p ';link;' \
     -o ${WORKING_FOLDER}/links.tsv.gz \
     -p ';alias;' \
     -o ${WORKING_FOLDER}/aliases.tsv.gz \
     -p ';description;' \
     -o ${WORKING_FOLDER}/descriptions.tsv.gz \
     -p ';label;' \
     -o ${WORKING_FOLDER}/labels.tsv.gz \
     -p ';count_distinct_properties,datatype;' \
     -o ${WORKING_FOLDER}/metadata.tsv.gz \
     --reject-file  ${WORKING_FOLDER}/claims_and_quals.tsv.gz \
     --use-mgzip --mgzip-threads 5

echo -e "\n*** Sort the claims and qualifiers file on the id column: ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     -i ${WORKING_FOLDER}/claims_and_quals.tsv.gz \
     -c id \
     -o ${WORKING_FOLDER}/claims_and_quals.sort-by-id.tsv.gz

echo -e "\n*** Sort the claims and qualifiers file on the node1 column: ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     -i ${WORKING_FOLDER}/claims_and_quals.tsv.gz \
     -c node1 \
     -o ${WORKING_FOLDER}/claims_and_quals.sort-by-node1.tsv.gz

echo -e "\n*** Split the claims and qualifiers into separate files. ***"
# If an edge has a node1 value that exists as an id value, then the
# edge is a qualifier, otherwise it is a claim.
time kgtk ${KGTK_OPTIONS} ifexists ${MGZIP_OPTIONS} \
     --input-file  ${WORKING_FOLDER}/claims_and_quals.sort-by-node1.tsv.gz \
     --input-keys node1 \
     --filter-file ${WORKING_FOLDER}/claims_and_quals.sort-by-id.tsv.gz \
     --filter-keys id \
     --output-file ${WORKING_FOLDER}/quals.tsv.gz \
     --reject-file ${WORKING_FOLDER}/claims.tsv.gz \
     --presorted --verbose

# The following step may not be needed:
echo -e "\n*** Ensure that the qualifier edges contain ID values. ***"
time kgtk ${KGTK_OPTIONS} add-id ${MGZIP_OPTIONS} --verbose \
     --id-prefix EQ \
     -i ${WORKING_FOLDER}/quals.tsv.gz \
     -o ${WORKING_FOLDER}/quals.with-ids.tsv.gz

# **************************************************************\
# Sort the different sections of the KG and deduplicate them.
# The deduplicated output is sorted, which should be helpful when
# the edges are loaded into the graph cache is a later script.
echo -e "\n*** Ensure that the aliases do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/aliases.tsv.gz \
     -o ${WORKING_FOLDER}/aliases.sorted.tsv.gz

echo -e "\n*** Ensure that the aliases do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/aliases.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/aliases.tsv.gz
 
echo -e "\n*** Ensure that the descriptions do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/descriptions.tsv.gz \
     -o ${WORKING_FOLDER}/descriptions.sorted.tsv.gz

echo -e "\n*** Ensure that the descriptions do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
                      --presorted --report-lists --verbose \
                      --columns node1 label node2 \
                      --keep-first id \
     -i ${WORKING_FOLDER}/descriptions.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/descriptions.tsv.gz
 
echo -e "\n*** Ensure that the labels do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/labels.tsv.gz \
     -o ${WORKING_FOLDER}/labels.sorted.tsv.gz

echo -e "\n*** Ensure that the labels do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/labels.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/labels.tsv.gz
 
echo -e "\n*** Ensure that the metadata do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/metadata.tsv.gz \
     -o ${WORKING_FOLDER}/metadata.sorted.tsv.gz

echo -e "\n*** Ensure that the metadata do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/metadata.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/metadata.tsv.gz

echo -e "\n*** Ensure that the claims do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/claims.tsv.gz \
     -o ${WORKING_FOLDER}/claims.sorted.tsv.gz

echo -e "\n*** Ensure that the claims do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/claims.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/claims.tsv.gz
 
echo -e "\n*** Ensure that the qualifiers do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/quals.with-ids.tsv.gz \
     -o ${WORKING_FOLDER}/quals.sorted.tsv.gz

echo -e "\n*** Ensure that the qualifiers do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/quals.sorted.tsv.gz \
     -o ${FINAL_PRODUCTS}/quals.tsv.gz \
|& tee ${WORKING_FOLDER}/quals-deduplicated.log
 
echo -e "\n*** The data files are ready to be loaded into the graph cache. ***"
