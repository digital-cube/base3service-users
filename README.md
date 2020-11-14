# base3service-users

requirements:
  - python3
  - postgresql
  - redis


in postgresql create database user demo, and using this user create databases demo and test_demo


perform following steps to run integration tests

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd config
cp config.local.yaml.sample config.local.yaml
cp config.docker.yaml.sample config.docker.yaml


./test.sh```