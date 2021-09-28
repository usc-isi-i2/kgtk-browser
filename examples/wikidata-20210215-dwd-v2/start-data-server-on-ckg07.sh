#! /bin/bash

# Run this from the KGTK browser top folder.

export FLASK_APP=kgtk_browser_app.py
export FLASK_ENV=development
export KGTK_BROWSER_CONFIG=examples/wikidata-20210215-dwd-v2/config_on_ckg07.py

flask run --host 0.0.0.0 --port 5009
