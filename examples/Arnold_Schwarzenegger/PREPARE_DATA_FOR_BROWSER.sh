#! /bin/bash

# Define some locations and options:

export INPUT_FILE="./data/Q2685.graph.all.tsv.gz"
export WORKING_FOLDER="./temp"
export GRAPHS="./graphs"

# These steps go by fairly fast.
# export KGTK_OPTIONS="--progress"
export KGTK_OPTIONS=""

export MGZIP_OPTIONS="--use-mgzip --mgzip-threads=5"

# If pigz is installed, use it for better sorting performance.
if [ -x "$(command -v pigz)" ]; then
    export GZIP_CMD="--gzip-command=pigz"
else
    export GZIP_CMD=""
fi

# Sort options, size these to your system.
export SORT_PARALLEL=20
export SORT_BUFFER_SIZE="25%"
export SORT_TEMP_FOLDER="./temp"

# Create the working, final products, and temporary folders:
mkdir -p ${WORKING_FOLDER}
mkdir -p ${GRAPHS}
mkdir -p ${SORT_TEMP_FOLDER}

# ******************************************************************
# Split the unified input file into:
#    aliases
#    descriptions
#    labels
#    metadata (datatypes)
#    claims and qualifiers
#
# Also split out "link" records, they shouldn't be there.
echo -e "\n*** Split the unified input file into parts. ***"
time kgtk ${KGTK_OPTIONS} filter ${MGZIP_OPTIONS} \
     -i ${INPUT_FILE} \
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
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     -i ${WORKING_FOLDER}/claims_and_quals.tsv.gz \
     -c id \
     -o ${WORKING_FOLDER}/claims_and_quals.sort-by-id.tsv.gz

echo -e "\n*** Sort the claims and qualifiers file on the node1 column: ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
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
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/aliases.tsv.gz \
     -o ${WORKING_FOLDER}/aliases.sorted.tsv.gz

echo -e "\n*** Ensure that the aliases do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/aliases.sorted.tsv.gz \
     -o ${GRAPHS}/aliases.tsv.gz
 
echo -e "\n*** Ensure that the descriptions do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/descriptions.tsv.gz \
     -o ${WORKING_FOLDER}/descriptions.sorted.tsv.gz

echo -e "\n*** Ensure that the descriptions do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
                      --presorted --report-lists --verbose \
                      --columns node1 label node2 \
                      --keep-first id \
     -i ${WORKING_FOLDER}/descriptions.sorted.tsv.gz \
     -o ${GRAPHS}/descriptions.tsv.gz
 
echo -e "\n*** Ensure that the labels do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/labels.tsv.gz \
     -o ${WORKING_FOLDER}/labels.sorted.tsv.gz

echo -e "\n*** Ensure that the labels do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/labels.sorted.tsv.gz \
     -o ${GRAPHS}/labels.tsv.gz
 
echo -e "\n*** Ensure that the metadata do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/metadata.tsv.gz \
     -o ${WORKING_FOLDER}/metadata.sorted.tsv.gz

echo -e "\n*** Ensure that the metadata do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 \
     --keep-first id \
     -i ${WORKING_FOLDER}/metadata.sorted.tsv.gz \
     -o ${GRAPHS}/metadata.tsv.gz

echo -e "\n*** Ensure that the claims do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/claims.tsv.gz \
     -o ${WORKING_FOLDER}/claims.sorted.tsv.gz

echo -e "\n*** Ensure that the claims do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/claims.sorted.tsv.gz \
     -o ${GRAPHS}/claims.tsv.gz
 
echo -e "\n*** Ensure that the qualifiers do not contain gross duplicates: sorting... ***"
time kgtk ${KGTK_OPTIONS} sort ${GZIP_CMD} ${MGZIP_OPTIONS} \
     -X "--parallel ${SORT_PARALLEL} --buffer-size ${SORT_BUFFER_SIZE} -T ${SORT_TEMP_FOLDER}" \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/quals.with-ids.tsv.gz \
     -o ${WORKING_FOLDER}/quals.sorted.tsv.gz

echo -e "\n*** Ensure that the qualifiers do not contain gross duplicates: deduplicating... ***"
time kgtk ${KGTK_OPTIONS} deduplicate ${MGZIP_OPTIONS} \
     --presorted --report-lists --verbose \
     --columns node1 label node2 id \
     -i ${WORKING_FOLDER}/quals.sorted.tsv.gz \
     -o ${GRAPHS}/quals.tsv.gz
 
echo -e "\n*** The data files are ready to be loaded into the graph cache. ***"
