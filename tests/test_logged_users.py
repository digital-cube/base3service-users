import http
import urllib.parse
from unittest.mock import patch


from base import store

from tests.helpers import BaseUserTest, token2user
from lookup.user_roles import ADMIN
from lookup.user_roles import SUPERUSER
from lookup.user_roles import DEVELOPER


class TestLoggedUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('base.src.base.token.token2user', token2user)
    def test_get_user_unauthorized(self):
        self.api(None, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('api.users_login.UsersLoginHandler.get_profile_image', return_value=None)
    def test_get_logged_users_data(self, *_):
        self.register_user(f'user', '123')

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'first_name', 'last_name'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('api.users_login.UsersLoginHandler.get_profile_image', return_value=None)
    def test_edit_user_data(self, *_):
        self.register_user('user', '123')

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _data = {
            'role_flags': SUPERUSER,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@other.com',
            'phone_number': '+22222222222',
            'language': 'de',
        }
        self.api(self.token, 'PATCH', f'{self.prefix}/me/change-data', body=_data, expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['changes'])

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('some@other.com', self.last_result['email'])
        self.assertEqual('First', self.last_result['first_name'])
        self.assertEqual('Last', self.last_result['last_name'])
        self.assertEqual('First Last', self.last_result['display_name'])
        self.assertEqual('+22222222222', self.last_result['phone'])
        self.assertEqual('some@other.com', self.last_result['email'])
        self.assertEqual('de', self.last_result['language'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('api.users_login.UsersLoginHandler.get_profile_image', return_value=None)
    def test_edit_user_username(self, *_):
        self.register_user('user', '123')
        _user_id = self.last_result['id']

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _login_data = {
            'username': 'user_new',
            'password': '1234',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        self.api(self.token, 'POST', f'{self.prefix}/me/change-username', body=_login_data, expected_code=http.HTTPStatus.UNAUTHORIZED)

        _login_data['password'] = '123'

        self.api(self.token, 'POST', f'{self.prefix}/me/change-username', body=_login_data, expected_code=http.HTTPStatus.NO_CONTENT)

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('user_new', self.last_result['username'])

        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.CREATED,
                 expected_result_contain_keys=['id', 'token'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('api.users_login.UsersLoginHandler.get_profile_image', return_value=None)
    def test_change_user_password(self, *_):
        self.register_user('user', '123')
        _user_id = self.last_result['id']

        self.api(self.token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _data = {
            'password': '1234',
            'new_password': '1234',
        }

        self.api(self.token, 'POST', f'{self.prefix}/me/change-password', body=_data, expected_code=http.HTTPStatus.UNAUTHORIZED)

        _data['password'] = '123'

        self.api(self.token, 'POST', f'{self.prefix}/me/change-password', body=_data, expected_code=http.HTTPStatus.NO_CONTENT)

        _login_data = {
            'username': 'user',
            'password': '123',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        _login_data['password'] = '1234'
        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.CREATED,
                 expected_result_contain_keys=['id', 'token'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False
