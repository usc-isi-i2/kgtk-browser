#! /bin/bash

# Run this from "examples/Arnold_Schwarznegger/"

export FLASK_APP=kgtk_browser_app.py
export FLASK_ENV=development
export KGTK_BROWSER_CONFIG=examples/faast/config_on_ckg07.py

cd ../..
flask run --host 0.0.0.0 --port 5006
