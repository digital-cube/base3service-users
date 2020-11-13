#!/usr/bin/env python
import os
import base
import importlib

if __name__ == "__main__":
    config = base.config
    my_dir_name = os.path.dirname(os.path.realpath(__file__))
    base.config.load_from_yaml(my_dir_name + f'/config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
    base.config.load_private_key(my_dir_name + '/keys/jwt.private_key')

    importlib.import_module('api.users')
    importlib.import_module('lookup.user_permissions')

    from base import store

    with open(my_dir_name + '/keys/jwt.public_key') as pubkey:
        store.set('users_service_public_key', pubkey.read())

    # with open(my_dir_name + '/keys/jwt.private_key') as pkey:
    #     store.set('users_service_private_key', pkey.read())

    base.run(debug=True)
