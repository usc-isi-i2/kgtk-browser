#! /bin/tcsh

# Start the npm server on ckg07.isi.edu

# Run this from "examples/faast/"

setenv HOST ckg07.isi.edu
setenv PORT 3000

cd app
npm start
