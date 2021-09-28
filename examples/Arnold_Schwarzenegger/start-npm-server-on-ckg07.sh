#! /bin/bash

# Start the npm server on ckg07.isi.edu

# Run this from "examples/Arnold_Schwarznegger/"

cd app
HOST=ckg07.isi.edu
export HOST
PORT=3008
export PORT
npm start
