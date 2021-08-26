#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG /data/rogers/kgtk-browser/kgtk_browser_config.py

flask run --host 0.0.0.0 --port 1775
