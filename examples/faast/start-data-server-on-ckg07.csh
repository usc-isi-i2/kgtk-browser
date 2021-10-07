#! /bin/tcsh

# Run this from "examples/Arnold_Schwarznegger/"

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG examples/faast/config_on_ckg07.py

cd ../..
flask run --host 0.0.0.0 --port 5008
