#!/bin/sh
pip install --upgrade pip
pip install wheel
pip install -e /base3
pip install mysqlclient

# .venv/bin/pip freeze > requirements.txt
