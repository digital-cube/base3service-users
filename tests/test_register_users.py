import http

from unittest.mock import patch

from base.src.base import store

from tests.helpers import BaseUserTest
from lookup.user_roles import USER
from lookup.alarm_types import ALARM1
from lookup.notification_type import EMAIL


class TestUsersAbout(BaseUserTest):

    def test_about(self):
        self.api(None, 'GET', self.prefix+'/about', expected_code=http.HTTPStatus.OK,
                 expected_result={"service": "users"})
        # self.show_last_result()


class TestRegisterUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_register_user(self):
        _data = {
            'user': {
                'username': 'user',
                'password': '123',
                'role_flags': USER,
            },
            'user_data': {
                'first_name': 'User',
                'last_name': 'Test'
            }
        }
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id', 'token'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def __TODO___test_register_user_with_minimum_data(self):
        _data = {
            'user': {
                'username': 'user',
                'password': '123',
            }
        }
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id', 'token'])
        # self.show_last_result()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_register_user_with_all_the_data(self):
        _data = {
            'user': {
                'username': 'user',
                'password': '123',
                'role_flags': USER,
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
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id', 'token'])
        # self.show_last_result()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_register_user_with_the_same_username(self):
        _data = {
            'user': {
                'username': 'user',
                'password': '123',
                'role_flags': USER,
            },
            'user_data': {
                'first_name': 'User',
                'last_name': 'Test'
            }
        }
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id', 'token'])
        # self.show_last_result()
        _data = {
            'user': {
                'username': 'user',
                'password': '123',
                'role_flags': USER,
            },
            'user_data': {
                'first_name': 'User',
                'last_name': 'Test'
            }
        }
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                 expected_result_subset={'message': 'Internal Server Error'})
        # self.show_last_result()

        _data = {
            'user': {
                'username': 'user2',
                'password': '123',
                'role_flags': USER,
            },
            'user_data': {
                'first_name': 'User2',
                'last_name': 'Test2'
            }
        }
        self.api(None, 'POST', self.prefix+'/register', body=_data, expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id', 'token'])
        # self.show_last_result()
