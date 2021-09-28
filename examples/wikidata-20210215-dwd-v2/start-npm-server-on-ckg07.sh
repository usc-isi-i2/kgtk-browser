#! /bin/bash

# Start the npm server on ckg07.isi.edu

# Run this from "examples/wikidata-20210215-dwd-v2/"

cd app
export HOST=ckg07.isi.edu
export PORT=3009
npm start
