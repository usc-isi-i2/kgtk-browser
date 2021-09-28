#! /bin/tcsh

# Start the npm server on ckg07.isi.edu

# Run this from "examples/Arnold_Schwarznegger/"

cd app
setenv HOST ckg07.isi.edu
setenv PORT 3008
npm start
