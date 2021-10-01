#! /bin/bash

# Run this from "examples/wikidata-20210215-dwd-v2/"

export FLASK_APP=kgtk_browser_app.py
export FLASK_ENV=development
export KGTK_BROWSER_CONFIG=examples/wikidata-20210215-dwd-v2/config_on_ckg07.py

export HOST=0.0.0.0
export PORT=5009

cd ../..
flask run --host ${HOST} --port ${PORT}
