#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG /home/rogers/kgtk/github/kgtk-browser/kgtk_browser_config.py

flask run
