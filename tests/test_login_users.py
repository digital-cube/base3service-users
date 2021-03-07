import http

from unittest.mock import patch

from base import store
from tests.helpers import token2user
from tests.helpers import BaseUserTest
from lookup.user_roles import USER
from lookup.alarm_types import ALARM1
from lookup.notification_type import EMAIL


class TestLoginUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_login_user(self):
        self.register_user('user', '123')

        _data = {
            'username': 'user',
            'password': '123',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_data, expected_code=http.HTTPStatus.CREATED,
                 expected_result_contain_keys=['id', 'token'])

    def test_login_non_existing_user(self):
        _data = {
            'username': 'user',
            'password': '123',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['id', 'message', 'method', 'uri', 'code'])
        # self.show_last_result()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_login_user_with_wrong_password(self):
        self.register_user('user', '123')

        _data = {
            'username': 'user',
            'password': '1234',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['id', 'message', 'method', 'uri', 'code'])
        # self.show_last_result()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_login_not_active_user(self):
        _data = {
            'active': False
        }
        self.register_user('user', '123', data=_data)

        _data = {
            'username': 'user',
            'password': '123',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['id', 'message', 'method', 'uri', 'code'])
        # self.show_last_result()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_check_users_session(self):
        self.register_user('user', '123')
        self.assertIn('token', self.last_result, 'Session token is present')
        self.api(self.last_result['token'], 'GET', self.prefix+'/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'first_name', 'last_name', 'active'])

        self.register_user('user2', '123')
        self.assertIn('token', self.last_result, 'Session token is present')
        self.api(self.last_result['token'], 'GET', self.prefix + '/session', expected_code=http.HTTPStatus.OK,
                 expected_result_subset={
                     # 'id': 'd5ce260a-5ad3-4026-938d-b56e35703a79',
                     'username': 'user2',
                     'first_name': 'User',
                     'last_name': 'Test',
                     'display_name': 'User Test',
                     'email': 'user@test.loc',
                     'active': True,
                     'alarm_type': ALARM1,
                     'notification_type': EMAIL,
                     'phone': '+33333333333'
                 })
        # self.show_last_result()
        # self.flush_db_at_the_end = False
