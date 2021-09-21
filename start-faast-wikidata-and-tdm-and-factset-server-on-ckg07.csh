#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG faast_wikidata-and-tdm-and-factset_config_on_ckg07.py

flask run --host 0.0.0.0 --port 5006
