#! /bin/tcsh

# Run this from "examples/wikidata-20210215-dwd-v2/"

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG examples/wikidata-20210215-dwd-v2/config_on_ckg07.py

setenv HOST 0.0.0.0
setenv PORT 5009

cd ../..
flask run --host ${HOST} --port ${PORT}
