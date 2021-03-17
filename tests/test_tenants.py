import http

from unittest.mock import patch

from base import store
from tests.helpers import BaseUserTest, token2user
from lookup.user_roles import SUPERUSER
from lookup.alarm_types import ALARM1
from lookup.notification_type import EMAIL


class TestTenants(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('base.src.base.token.token2user', token2user)
    def test_add_tenant_as_non_authorized_user(self, *_):
        _data = {
            'tenant': {
                'name': 'Tenant'
            }
        }
        self.api(None, 'POST', self.prefix+'/tenants', body=_data, expected_code=http.HTTPStatus.UNAUTHORIZED,
                 expected_result_contain_keys=['message'])

        self.register_user('user', '123')
        self.api(self.last_result['token'], 'POST', self.prefix+'/tenants', body=_data,
                 expected_code=http.HTTPStatus.UNAUTHORIZED, expected_result_contain_keys=['message'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_add_tenant(self):
        self.register_user('user', '123', role_flags=SUPERUSER)

        _data = {
            'tenant': {
                'name': 'Tenant'
            }
        }
        self.api(self.last_result['token'], 'POST', self.prefix+'/tenants', body=_data,
                 expected_code=http.HTTPStatus.CREATED, expected_result_contain_keys=['id'])
        self.assertIsNotNone(self.last_result['id'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    @patch('base.src.base.token.token2user', token2user)
    def test_get_tenants_unauthorized(self, *_):
        self.api(None, 'GET', self.prefix+'/tenants', expected_code=http.HTTPStatus.UNAUTHORIZED)

        self.register_user('user', '123')
        _token = self.last_result['token']

        self.api(_token, 'GET', self.prefix+'/tenants', expected_code=http.HTTPStatus.UNAUTHORIZED)
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_get_tenants(self):
        self.register_user('user', '123', role_flags=SUPERUSER)
        _token = self.last_result['token']
        self.add_tenant()

        self.api(_token, 'GET', self.prefix+'/tenants', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['tenants'])
        _tenants = self.last_result['tenants']
        self.assertEqual(1, len(_tenants))
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_get_tenant(self):
        self.register_user('user', '123', role_flags=SUPERUSER)
        _token = self.last_result['token']
        self.add_tenant()
        _id = self.last_result['id']

        self.api(_token, 'GET', f'{self.prefix}/tenants/{_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'name', 'created'])
        self.assertEqual('Tenant', self.last_result['name'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_edit_tenant(self):
        self.register_user('user', '123', role_flags=SUPERUSER)
        _token = self.last_result['token']
        self.add_tenant()
        _id = self.last_result['id']

        _data = {
            'new_tenant': {
                'name': 'New Tenant'
            }
        }
        self.api(_token, 'PUT', f'{self.prefix}/tenants/{_id}', body=_data, expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['changes'])

        self.api(_token, 'GET', f'{self.prefix}/tenants/{_id}', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['id', 'name', 'created'])
        self.assertEqual('New Tenant', self.last_result['name'])
        # self.show_last_result()
        # self.flush_db_at_the_end = False

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_add_user_to_tenant(self):
        self.register_user('user', '123', role_flags=SUPERUSER)
        _token = self.last_result['token']
        _id_superuser = self.last_result['id']
        self.add_tenant()
        _id = self.last_result['id']
        self.register_user('user2', '123')
        _id_user = self.last_result['id']
        _token_user = self.last_result['token']

        self.api(_token, 'POST', f'{self.prefix}/tenants/{_id}', body={'user': _id_user}, expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_token, 'POST', f'{self.prefix}/tenants/{_id}', body={'user': _id_superuser}, expected_code=http.HTTPStatus.NO_CONTENT)

        self.api(_token, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['tenant'])
        self.assertEqual('Tenant', self.last_result['tenant']['name'])
        self.api(_token_user, 'GET', f'{self.prefix}/session', expected_code=http.HTTPStatus.OK,
                 expected_result_contain_keys=['tenant'])
        self.assertEqual('Tenant', self.last_result['tenant']['name'])

        # self.show_last_result()
        # self.flush_db_at_the_end = False
