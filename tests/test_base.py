from base import test
import unittest
import importlib

import os
from base import http

current_file_folder = os.path.dirname(os.path.realpath(__file__))


# from unittest.mock import patch


class SetUpTestUserServiceBase(test.BaseTest):

    def setUp(self):
        from base import registry, orm, app, config
        config.load_from_yaml(os.path.dirname(os.path.realpath(__file__)) + f'/../config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
        config.conf['db']['database'] = f"test_{config.conf['db']['database']}"

        print(config.conf['mysql'])

        self.prefix = config.conf['prefix']

        importlib.import_module('orm.models')
        registry.test = True

        orm = orm.init_orm(config.conf['db'])

        orm.clear_database()
        orm.create_db_schema()

        importlib.import_module('api.users')
        importlib.import_module('api.tc_users')

        config.init_logging()
        self.my_app = app.make_app(debug=True)

        from base import store
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../keys/jwt.public_key') as pubkey:
            store.set('users_service_public_key', pubkey.read())

        config.load_private_key(os.path.dirname(os.path.realpath(__file__)) + '/../keys/jwt.private_key')

        super().setUp()
        registry.test_port = self.get_http_port()

    def register_and_login(self, username, password, permission_flags):
        self.api(None, 'POST', self.prefix + '/',
                 body={'user': {'username': username,
                                'password': password,
                                'permission_flags': permission_flags}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'}
                 )

        _id = self.last_result['id']

        self.api(None, 'POST', self.prefix + '/sessions/',
                 body={'username': username,
                       'password': password},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id', 'token'}
                 )

        _token = self.last_result['token']

        return _id, _token

if __name__ == '__main__':
    unittest.main()
