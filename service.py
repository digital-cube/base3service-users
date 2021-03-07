#!/usr/bin/env python
import os
import base

if __name__ == '__main__':

    current_file_folder = os.path.dirname(os.path.realpath(__file__))
    base.config.load_from_yaml(f'{current_file_folder}/config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')

    # config.init_logging()

    with open(f'{current_file_folder}/keys/users.key.pem') as pubkey:
        base.store.set('users_service_public_key', pubkey.read())

    base.config.load_private_key(f'{current_file_folder}/keys/users.key')

    base.run(print_app_info=True, print_routes=True)
