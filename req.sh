rm -rf .venv
python3 -m venv .venv

pip install --upgrade pip
pip install wheel
pip install faker
pip install asynctest
pip install -e /base3
pip install -e /shared
pip install pycurl --global-option="--with-openssl"
