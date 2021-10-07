#! /bin/bash

# export INPUT_FILE="Q2685.graph.all.small.tsv.gz"
# export INPUT_FILE="Q2685.graph.all.tsv.gz"
export INPUT_FILE="arnold.all.tsv.gz"

mkdir -p data
rclone copy kgtk:iswc2021tutorial/datasets/${INPUT_FILE} data/
