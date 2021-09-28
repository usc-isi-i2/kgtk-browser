#! /bin/bash

mkdir -p data
rclone copy kgtk:/datasets/wikidata-20210215-dwd-v2/all.tsv.gz data/
