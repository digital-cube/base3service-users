import unittest
from base import http, test
from tests.test_base import SetUpTestUserServiceBase

THE_PASSWORD = 'SomePassword123!'

import lookup.user_permissions as perm

from unittest.mock import patch

from tests.test_users import SetuUpTestUsersWithRegisteredAdmin

class TestInfo(SetuUpTestUsersWithRegisteredAdmin):

    def test_info(self):
        self.api(None, 'GET', self.prefix + '/info')

    def test_users_by_org_unit(self):
        self.api(self.token_admin, 'GET', self.prefix + '/by-org-units', expected_code=http.status.OK)
        #TODO: Test

    def test_one_portal_all_users(self):
        self.api(self.token_admin, 'POST', '/tcapi/users/one-portal-users', expected_code=http.status.OK, expected_result_contain_keys={'added'})

    def test_fetch_user(self):

        self.id_igor, self.token_igor = self.register_and_login('igor', THE_PASSWORD, perm.USER)
        self.api(None, 'GET', f'/tcapi/users/admin/{self.id_igor}', expected_code=http.status.UNAUTHORIZED)
        self.api(self.token_admin, 'GET', f'/tcapi/users/{self.id_igor}') #, expected_code=http.status.OK)
