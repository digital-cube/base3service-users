# SIGRE OpenWaste Users service

## Start tests
```bash
cd users
. venv.sh
python3 tests/start_all_tests.py
```

## Generate authentication keypair:
```bash
ssh-keygen -t rsa -b 4096 -m pem -f __path_to_file_with_priv_key__
ssh-keygen -f __path_to_file_with_priv_key__.pub -e -m pem > __path_to_file_with_priv_key__.pem
```
- remove the one with '.pub' extension

## Initialize database
```bash
cd users # or other service
. venv.sh
aerich init -t config.config.TORTOISE_ORM
aerich --app=users init-db 
```
