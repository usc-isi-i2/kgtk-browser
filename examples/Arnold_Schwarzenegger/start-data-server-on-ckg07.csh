#! /bin/tcsh

setenv FLASK_APP kgtk_browser_app.py
setenv FLASK_ENV development
setenv KGTK_BROWSER_CONFIG examples/Arnold_Schwarzenegger/config_on_ckg07.py

flask run --host 0.0.0.0 --port 5008
