import http
import urllib.parse
from unittest.mock import patch


from base import store

from tests.helpers import BaseUserTest
from lookup.user_roles import ADMIN
from lookup.user_roles import SUPERUSER
from lookup.user_roles import DEVELOPER


class TestLoggedUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_get_user_unauthorized(self):
        self.api(None, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_get_logged_users_data(self):
        self.register_user(f'user', '123')

        self.api(self.token, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'first_name', 'last_name'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    def test_edit_user_data(self):
        self.register_user('user', '123')

        self.api(self.token, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _data = {
            'role_flags': SUPERUSER,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@other.com',
            'phone_number': '+22222222222',
        }
        self.api(self.token, 'PATCH', f'{self.prefix}/me', body=_data, expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['changes'])

        self.api(self.token, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('some@other.com', self.last_result['email'])
        self.assertEqual('First', self.last_result['first_name'])
        self.assertEqual('Last', self.last_result['last_name'])
        self.assertEqual('First Last', self.last_result['display_name'])
        self.assertEqual('+22222222222', self.last_result['phone'])
        self.assertEqual('some@other.com', self.last_result['email'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    def test_edit_user_username_and_password(self):
        self.register_user('user', '123')
        _user_id = self.last_result['id']
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']

        self.api(self.token, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _login_data = {
            'username': 'user_new',
            'password': '1234',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        self.api(self.token, 'POST', f'{self.prefix}/me', body=_login_data, expected_code=http.HTTPStatus.NO_CONTENT)

        self.api(self.token, 'GET', f'{self.prefix}/me', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('user_new', self.last_result['username'])

        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.CREATED,
                 expected_result_contain_keys=['id', 'token'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False
