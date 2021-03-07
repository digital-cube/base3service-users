import http
from unittest.mock import patch


import base
from base import store
from tests.helpers import BaseUserTest
from lookup.user_roles import ADMIN


class TestUsersScopes(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_get_available_scopes(self):
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']
        _admin_id = self.last_result['id']

        self.api(_admin_token, 'GET', f'{self.prefix}/users-scopes', expected_code=http.HTTPStatus.OK,
                 expected_result={'scopes': ['OPENCOUNTER', 'OPENLIGHT', 'OPENWASTE', 'OPENWATER']})

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_add_scopes_to_users_unauthorized(self):
        self.register_user('user', '123')
        _data = {
            'scope': {
                'NoName': 2
            }
        }
        self.api(self.last_result['token'], 'POST', f'{self.prefix}/users-scopes/1', body=_data,
                 expected_code=http.HTTPStatus.UNAUTHORIZED, expected_result_contain_keys=['message'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_add_scopes_to_users(self):
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']
        _admin_id = self.last_result['id']
        self.register_user('user', '123')
        _user_token = self.last_result['token']
        _user_id = self.last_result['id']
        _data = {
            'scopes': {
                'NoName': base.scope_permissions.READ
            }
        }
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_user_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_admin_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)

        self.api(_user_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertEqual(base.scope_permissions.READ, self.last_result['scopes']['NoName'])
        self.api(_admin_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertEqual(base.scope_permissions.READ, self.last_result['scopes']['NoName'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_edit_scopes_for_users(self):
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']
        _admin_id = self.last_result['id']
        _data = {
            'scopes': {
                'NoName': base.scope_permissions.READ
            }
        }
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_admin_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_admin_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertEqual(base.scope_permissions.READ, self.last_result['scopes']['NoName'])

        _data = {
            'scopes': {
                'NoName': base.scope_permissions.ALL
            }
        }
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_admin_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_admin_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertEqual(base.scope_permissions.ALL, self.last_result['scopes']['NoName'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_remove_scopes_for_users(self):
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']
        _admin_id = self.last_result['id']
        _data = {
            'scopes': {
                'NoName': base.scope_permissions.READ
            }
        }
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_admin_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_admin_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertEqual(base.scope_permissions.READ, self.last_result['scopes']['NoName'])

        _data = {'scopes': {}}
        self.api(_admin_token, 'POST', f'{self.prefix}/users-scopes/{_admin_id}', body=_data,
                 expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_admin_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['scopes'])
        self.assertIsNone(self.last_result['scopes'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False
