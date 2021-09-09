#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG /home/rogers/kgtk/github/kgtk-browser/faast_wikidata-and-tdm_config.py

flask run --port 5002
