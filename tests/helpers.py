import os
from unittest.mock import patch

import base
from base import test
from base import registry, app, config
from base import store
from base import http
from tortoise.contrib.test import initializer, finalizer

from lookup.user_roles import USER
from lookup.alarm_types import ALARM1
from lookup.notification_type import EMAIL

import sys
# print("USING",  sys.executable)

current_file_folder = os.path.dirname(os.path.realpath(__file__))
root_folder = os.path.abspath(os.path.join(current_file_folder, '..'))

random_uuid = '00000000-0000-0000-0420-000000000000'
id_user = '00000000-0000-0000-0000-000000000001'
id_session = '00000000-0000-0000-0000-000000000002'


def token2user(_):
    return {
        'id': id_session,
        'id_user': id_user,
        'permissions': 0
    }


class BaseUserTest(test.BaseTest):

    def setUp(self):
        self.flush_db_at_the_end = True     # flush db on the tearDown. Set this to False in test not to flush db

        import os
        config.load_from_yaml(current_file_folder + f'/../config/config.{os.getenv("ENVIRONMENT", "local")}.yaml')
        config.conf['test'] = True

        from base import store
        # store engine has to be patched not to use redis and not to change the config option
        with patch('base.store.Store.engine', store.DictStore()):

            asyncio_current_loop = self.get_new_ioloop()
            asyncio_current_loop.run_sync(app.init_orm)

            _models = config.conf['tortoise']['apps'][base.config.conf['name']]['models']
            _db_url = base.config.get_db_url(test=True)

            initializer(_models, app_label=base.config.conf['name'], db_url=_db_url, loop=asyncio_current_loop.asyncio_loop)

            registry.test = True

            self.prefix = config.conf['prefix']

            config.init_logging()
            config.conf['verbose'] = False
            self.my_app = app.make_app(debug=True)

            with open(f'{root_folder}/keys/users.key.pem') as pubkey:
                store.set('users_service_public_key', pubkey.read())

            config.load_private_key(f'{root_folder}/keys/users.key')

            super().setUp()
            registry.test_port = self.get_http_port()

        # base.route.print_all_routes()

    def tearDown(self) -> None:

        _flush_db = not hasattr(self, 'flush_db_at_the_end') or self.flush_db_at_the_end
        if _flush_db:
            finalizer()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def register_user(self, username, password, data=None, user_data=None, role_flags=USER):
        _data = {
            'user': {
                'username': username,
                'password': password,
                'role_flags': role_flags
            },
            'user_data': {
                'first_name': 'User',
                'last_name': 'Test',
                'email': 'user@test.loc',
                'notification_type': EMAIL,
                'alarm_type': ALARM1,
                'phone': '+33333333333',
            }
        }
        if data:
            _data['user'].update(data)
        if user_data:
            _data['user_data'].update(data)

        self.api(None, 'POST', f'{self.prefix}/register', body=_data, expected_code=http.status.CREATED,
                 expected_result_contain_keys=['id', 'token'])

        self.token = self.last_result['token']

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def add_tenant(self, name='Tenant'):
        _data = {
            'tenant': {
                'name': name
            }
        }
        self.api(self.last_result['token'], 'POST', self.prefix+'/tenants', body=_data,
                 expected_code=http.status.CREATED, expected_result_contain_keys=['id'])
        self.assertIsNotNone(self.last_result['id'])
        return self.last_result
