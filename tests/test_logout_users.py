import http

from unittest.mock import patch

from base import store
from tests.helpers import BaseUserTest


class TestLogoutUsers(BaseUserTest):

    @patch('base.store.Store.engine', store.DictStore())        # has to be patched not to use redis without the config
    def test_logout_user(self):
        self.register_user('user', '123')
        self.assertIn('token', self.last_result, 'Session token is present')
        _token = self.last_result['token']

        self.api(_token, 'DELETE', self.prefix+'/session', expected_code=http.HTTPStatus.NO_CONTENT)
        self.api(_token, 'DELETE', self.prefix+'/session', expected_code=http.HTTPStatus.UNAUTHORIZED)
        self.api(_token, 'GET', self.prefix+'/session', expected_code=http.HTTPStatus.UNAUTHORIZED)
        # self.show_last_result()
        # self.flush_db_at_the_end = False
