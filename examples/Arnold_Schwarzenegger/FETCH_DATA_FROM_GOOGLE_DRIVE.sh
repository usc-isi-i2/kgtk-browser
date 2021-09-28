#! /bin/bash

mkdir -p data
rclone copy kgtk:iswc2021tutorial/datasets/Q2685.graph.all.tsv.gz data/
