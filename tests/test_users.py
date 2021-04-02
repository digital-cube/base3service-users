import http
import urllib.parse
from unittest.mock import patch


from base import store

from tests.helpers import BaseUserTest, token2user
from lookup.user_roles import ADMIN
from lookup.user_roles import SUPERUSER
from lookup.user_roles import DEVELOPER


class TestUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    def test_get_users_unauthorized(self, *_):
        with patch('base.src.base.token.token2user', return_value=None):
            self.api(None, 'GET', f'{self.prefix}', expected_code=http.HTTPStatus.UNAUTHORIZED,
                     expected_result_contain_keys=['message'])

        self.register_user('user', '123')
        self.api(self.last_result['token'], 'GET', f'{self.prefix}', expected_code=http.HTTPStatus.OK)

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def add_users(self):
        self.users = {}
        self.users_ids = []
        for i in range(2):
            self.register_user(f'user{i}', '123')
            self.users[self.last_result['id']] = self.last_result['token']
            self.users_ids.append(self.last_result['id'])

        self.admins = {}
        self.admins_ids = []
        for i in range(2):
            self.register_user(f'admin{i}', '123', role_flags=ADMIN)
            self.admins[self.last_result['id']] = self.last_result['token']
            self.admins_ids.append(self.last_result['id'])

        self.superusers = {}
        self.superusers_ids = []
        for i in range(2):
            self.register_user(f'superuser{i}', '123', role_flags=SUPERUSER)
            self.superusers[self.last_result['id']] = self.last_result['token']
            self.superusers_ids.append(self.last_result['id'])

        self.developers = {}
        self.developers_ids = []
        for i in range(2):
            self.register_user(f'developer{i}', '123', role_flags=DEVELOPER)
            self.developers[self.last_result['id']] = self.last_result['token']
            self.developers_ids.append(self.last_result['id'])

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_add_users(self):
        self.add_users()

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    def test_get_users(self, *_):
        self.add_users()

        self.api(self.admins[self.admins_ids[0]], 'GET', self.prefix, expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['users'])
        _users = self.last_result['users']
        self.assertEqual(8, len(_users))

        _params = urllib.parse.urlencode({
            'limit': 3,
            'offset': 0
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['users'])
        _users = self.last_result['users']
        self.assertEqual(3, len(_users))

        _params = urllib.parse.urlencode({
            'limit': 3,
            'offset': 3
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['users'])
        _users = self.last_result['users']
        self.assertEqual(3, len(_users))

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    def test_get_users_with_order(self, *_):
        self.add_users()

        _params = urllib.parse.urlencode({
            'order_by': 'nonexisting_key'
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}',
                 expected_code=http.HTTPStatus.BAD_REQUEST, expected_result_subset={'message': 'Invalid order key'})

        _params = urllib.parse.urlencode({
            'order_by': 'username'
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}',
                 expected_code=http.HTTPStatus.OK, expected_result_contain_keys=['users'])
        self.assertEqual(8, len(self.last_result['users']))

        _params = urllib.parse.urlencode({
            'order_by': 'email'
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['users'])
        self.assertEqual(8, len(self.last_result['users']))

        _params = urllib.parse.urlencode({
            'order_by': 'first_name'
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}',
                 expected_code=http.HTTPStatus.OK, expected_result_contain_keys=['users'])
        self.assertEqual(8, len(self.last_result['users']))

        _params = urllib.parse.urlencode({
            'order_by': 'last_name'
        })
        self.api(self.admins[self.admins_ids[0]], 'GET', f'{self.prefix}?{_params}',
                 expected_code=http.HTTPStatus.OK, expected_result_contain_keys=['users'])
        self.assertEqual(8, len(self.last_result['users']))

        # self.show_last_result()
        # self.flush_db_at_the_end = False


class TestUser(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    def test_get_user_data_for_invalid_user_id(self):
        self.register_user('admin', '123', role_flags=ADMIN)
        self.api(self.last_result['token'], 'GET', f'{self.prefix}/1', expected_code=http.HTTPStatus.BAD_REQUEST,
                 expected_result_subset={'message': 'Invalid data 1 for id AuthUser or AuthUser not found'})
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('base.src.base.token.token2user', token2user)
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    def test_get_user_unauthorized(self, *_):
        with patch('base.src.base.token.token2user', return_value=None):
            self.api(None, 'GET', f'{self.prefix}/1', expected_code=http.HTTPStatus.UNAUTHORIZED,
                     expected_result_contain_keys=['message'])
        self.register_user('user', '123')
        _id = self.last_result['id']

        self.api('x', 'GET', f'{self.prefix}/00000000-0000-0000-0000-000000000000', expected_code=http.HTTPStatus.NOT_FOUND,
                 expected_result_contain_keys=['message'])
        self.api('x', 'GET', f'{self.prefix}/{_id}', expected_code=http.HTTPStatus.OK)
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    def test_get_user(self):
        self.register_user('user', '123')
        _user_id = self.last_result['id']
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']

        self.api(_admin_token, 'GET', f'{self.prefix}/{_user_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    def test_edit_user_data(self, *_):
        self.register_user('user', '123')
        _user_id = self.last_result['id']
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']

        self.api(_admin_token, 'GET', f'{self.prefix}/{_user_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        _data = {
            'user': _user_id,
            'role_flags': SUPERUSER,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@other.com',
            'alarm_type': 2,
            'notification_type': 2,
            'phone_number': '+22222222222',
            'active': False,
            'last_used_application': 'WASTE'
        }
        self.api(_admin_token, 'PATCH', f'{self.prefix}/{_user_id}', body=_data, expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['changes'])

        self.api(_admin_token, 'GET', f'{self.prefix}/{_user_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('user', self.last_result['username'])
        self.assertEqual('some@other.com', self.last_result['email'])
        self.assertEqual('First', self.last_result['first_name'])
        self.assertEqual('Last', self.last_result['last_name'])
        self.assertEqual('First Last', self.last_result['display_name'])
        self.assertEqual(SUPERUSER, self.last_result['role_flags'])
        self.assertIsNotNone(self.last_result['data'])
        self.assertIn('last_used_application', self.last_result['data'])
        self.assertEqual('WASTE', self.last_result['data']['last_used_application'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())  # has to be patched not to use redis without the config
    @patch('api.users.get_documents_for_an_instance', return_value=([], None))
    @patch('api.users_login.UsersLoginHandler.get_profile_image', return_value=None)
    def test_edit_user_username_and_password(self, *_):
        self.register_user('user', '123')
        _user_id = self.last_result['id']
        self.register_user('admin', '123', role_flags=ADMIN)
        _admin_token = self.last_result['token']

        self.api(_admin_token, 'GET', f'{self.prefix}/{_user_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])
        self.assertEqual('user', self.last_result['username'])

        _login_data = {
            'username': 'user_new',
            'password': '1234',
        }
        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        _data = {
            'user': _user_id,
            'username': 'user_new',
            'password': '1234'
        }
        self.api(_admin_token, 'POST', f'{self.prefix}/{_user_id}', body=_data, expected_code=http.HTTPStatus.NO_CONTENT)

        self.api(_admin_token, 'GET', f'{self.prefix}/{_user_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'username', 'email', 'first_name', 'last_name', 'display_name'])

        self.assertEqual('user_new', self.last_result['username'])

        self.api(None, 'POST', self.prefix+'/session', body=_login_data, expected_code=http.HTTPStatus.CREATED,
                 expected_result_contain_keys=['id', 'token'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False
