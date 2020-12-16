#!/bin/sh
pip install --upgrade pip
pip install wheel
pip install -e /base3
pip install pycurl --global-option="--with-openssl"
 
# .venv/bin/pip freeze > requirements.txt
