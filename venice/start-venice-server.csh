#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG /home/rogers/kgtk/github/kgtk-browser/venice/venice-config.py

flask run --port 5007
