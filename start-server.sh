#! /bin/sh

export FLASK_APP kgtk_browser_app.py
export FLASK_ENV development
export KGTK_BROWSER_CONFIG /home/rogers/kgtk/github/kgtk-browser/kgtk_browser_config.py

flask run
