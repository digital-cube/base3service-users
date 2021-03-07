rm -rf .venv
python3 -m venv .venv

.venv/bin/pip install --upgrade pip
.venv/bin/pip install wheel
.venv/bin/pip install -e ../base3
.venv/bin/pip install -e ../shared
.venv/bin/pip install faker
.venv/bin/pip install asynctest
.venv/bin/pip install pycurl --global-option="--with-openssl"
