#! /bin/bash

# Run this from the KGTK browser top folder.

FLASK_APP=kgtk_browser_app.py
export FLASK_APP

FLASK_ENV=development
export FLASK_ENV

KGTK_BROWSER_CONFIG=examples/Arnold_Schwarzenegger/config_on_ckg07.py
export KGTK_BROWSER_CONFIG

flask run --host 0.0.0.0 --port 5008
