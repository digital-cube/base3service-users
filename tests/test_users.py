import unittest
from base import http, test
from tests.test_base import SetUpTestUserServiceBase

THE_PASSWORD = 'SomePassword123!'

import lookup.user_permissions as perm

from unittest.mock import patch


class TestUsersCreatingAdminUser(SetUpTestUserServiceBase):

    def test_unauthorized_user_tries_to_fetch_list_of_all_users(self):
        self.api(None, 'GET', self.prefix() + '/admin', expected_code=http.status.UNAUTHORIZED)
        self.api('INVALIDTOKEN', 'GET', self.prefix() + '/admin', expected_code=http.status.UNAUTHORIZED)

    def test_tries_to_initially_register_admin_user_after_non_admin_users_has_been_registered(self):
        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'user',
                                'password': THE_PASSWORD}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'}
                 )

        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'admin',
                                'password': THE_PASSWORD,
                                'permission_flags': perm.ADMIN}},
                 expected_code=http.status.UNAUTHORIZED,
                 expected_result_subset={'id': 'NOT_ALLOWED_TO_REGISTER_ADMIN_USER'})

    def test_register_initial_admin_user(self):
        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'admin',
                                'password': THE_PASSWORD,
                                'permission_flags': perm.ADMIN}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'}
                 )


class SetuUpTestUsersWithRegisteredAdmin(SetUpTestUserServiceBase):

    def setUp(self):
        super().setUp()

        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'admin',
                                'password': THE_PASSWORD,
                                'permission_flags': perm.ADMIN}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'}
                 )

        self.id_admin = self.last_result['id']

        self.api(None, 'POST', self.prefix() + '/sessions/',
                 body={'username': 'admin',
                       'password': THE_PASSWORD},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id', 'token'}
                 )

        self.token_admin = self.last_result['token']


class TestUsersWithRegisteredAdmin(SetuUpTestUsersWithRegisteredAdmin):

    def test_admin_fetch_list_of_users(self):
        self.api(self.token_admin, 'GET', self.prefix() + '/admin',
                 expected_code=http.status.OK,
                 expected_result_contain_keys={"summary", "users"},
                 expected_result_subset={"summary": {
                     "total_pages": 1,
                     "total_items": 1,
                     "page": 1,
                     "per_page": 10,
                     "next": None,
                     "previous": None
                 }}
                 )

    def test_admin_fetch_own_info(self):
        self.api(self.token_admin, 'GET', self.prefix() + '/', expected_code=http.status.OK,
                 expected_result_subset={
                     "username": "admin",
                     "email": None,
                     "permission_flags": 2,
                     "first_name": None,
                     "last_name": None
                 })

    def test_create_user_and_apply_admin_role(self):
        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'new_admin',
                                'password': THE_PASSWORD,
                                'permission_flags': perm.ADMIN}},
                 expected_code=http.status.UNAUTHORIZED,
                 expected_result_subset={'id': 'NOT_ALLOWED_TO_REGISTER_ADMIN_USER'})

        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'new_admin',
                                'password': THE_PASSWORD}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'})

        id_new_admin = self.last_result['id']

        # fetch all users
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin', expected_code=http.status.OK,
                 expected_result_subset={
                     "summary": {
                         "total_pages": 1,
                         "total_items": 2,
                         "page": 1,
                         "per_page": 10,
                         "next": None,
                         "previous": None
                     }})

        # fetch all admins / expecting just one
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin?permission_flags={perm.ADMIN}',
                 expected_code=http.status.OK,
                 expected_result_subset={
                     "summary": {
                         "total_pages": 1,
                         "total_items": 1,
                         "page": 1,
                         "per_page": 10,
                         "next": None,
                         "previous": None
                     }})

        # fetch all non admins / expecting just one
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin?permission_flags={perm.USER}',
                 expected_code=http.status.OK,
                 expected_result_subset={
                     "summary": {
                         "total_pages": 1,
                         "total_items": 1,
                         "page": 1,
                         "per_page": 10,
                         "next": None,
                         "previous": None
                     }})

        # transform user into admin
        self.api(self.token_admin, 'PATCH', self.prefix() + f'/admin/{id_new_admin}', body={'data': {
            'permission_flags': perm.USER | perm.ADMIN
        }}, expected_result=["permission_flags"])

        # fetch all admins / expecting 2 users
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/?permission_flags={perm.ADMIN}',
                 expected_code=http.status.OK,
                 expected_result_subset={
                     "summary": {
                         "total_pages": 1,
                         "total_items": 2,
                         "page": 1,
                         "per_page": 10,
                         "next": None,
                         "previous": None
                     }})

        # fetch all non admins users
        # still expecting 1 users, because new_admin is user and admin too.
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/?permission_flags={perm.USER}',
                 expected_code=http.status.OK,
                 expected_result_subset={
                     "summary": {
                         "total_pages": 1,
                         "total_items": 1,
                         "page": 1,
                         "per_page": 10,
                         "next": None,
                         "previous": None
                     }})


class TestUsersWithRegisteredAdminAndTwoNonAdminUsers(SetuUpTestUsersWithRegisteredAdmin):

    def setUp(self):
        super().setUp()

        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'user',
                                'password': THE_PASSWORD}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'})

        self.id_user = self.last_result['id']

        self.api(None, 'POST', self.prefix() + '/sessions/',
                 body={'username': 'user', 'password': THE_PASSWORD},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'token', 'id'})

        self.token_user = self.last_result['token']

        self.api(None, 'POST', self.prefix() + '/',
                 body={'user': {'username': 'user2',
                                'password': THE_PASSWORD}},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id'})

        self.id_user2 = self.last_result['id']

        self.api(None, 'POST', self.prefix() + '/sessions/',
                 body={'username': 'user2', 'password': THE_PASSWORD},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'token', 'id'})

        self.token_user2 = self.last_result['token']

    def test_user_change_preferences(self):
        # user changes his basic properties
        self.api(self.token_user, 'PATCH', self.prefix() + f'/', body={
            'data': {'first_name': 'John',
                     'last_name': 'Doe',
                     'email': 'johndoe@example.com'}},
                 expected_code=http.status.OK,
                 expected_result=["email", "first_name", "last_name"])

        # basic user (user) tries to change other user (user2) basic properties
        self.api(self.token_user, 'PATCH', self.prefix() + f'/admin/{self.id_user2}', body={
            'data': {'first_name': 'John2',
                     'last_name': 'Doe2',
                     'email': 'johndoe2@example.com'}},
                 expected_code=http.status.UNAUTHORIZED)

        # admin user changes other user (user2) basic properties
        self.api(self.token_admin, 'PATCH', self.prefix() + f'/admin/{self.id_user2}', body={
            'data': {'first_name': 'John2',
                     'last_name': 'Doe2',
                     'email': 'johndoe2@example.com'}},
                 expected_code=http.status.OK,
                 expected_result=["email", "first_name", "last_name"])

    def test_user_change_own_password(self):
        # user tries to change password without providing old one
        self.api(self.token_user, 'PATCH', self.prefix() + f'/', body={
            'data': {'password': THE_PASSWORD + '-updated'}},
                 expected_code=http.status.UNAUTHORIZED,
                 expected_result_subset={"id": "MISSING_PARAM_OLD_PASSWORD"})

        # user tries to change his password by providing incorect old password
        self.api(self.token_user, 'PATCH', self.prefix() + f'/', body={
            'data': {'old_password': THE_PASSWORD + '-incorect',
                     'password': THE_PASSWORD + '-updated'}},
                 expected_code=http.status.UNAUTHORIZED)

        # user successfully changes his password by providing old one
        self.api(self.token_user, 'PATCH', self.prefix() + f'/', body={
            'data': {'old_password': THE_PASSWORD,
                     'password': THE_PASSWORD + '-updated'}},
                 expected_code=http.status.OK)

        # try to login user with old password
        self.api(None, 'POST', self.prefix() + '/sessions', body={'username': 'user',
                                                                  'password': THE_PASSWORD},
                 expected_code=http.status.UNAUTHORIZED)

        # try to login user with new password
        self.api(None, 'POST', self.prefix() + '/sessions', body={'username': 'user',
                                                                  'password': THE_PASSWORD + '-updated'},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id', 'token'})

        # admin changes password for target user without providing old password
        self.api(self.token_admin, 'PATCH', self.prefix() + f'/admin/{self.id_user}', body={
            'data': {'password': 'a'}},
                 expected_code=http.status.OK,
                 expected_result=["password"])

        # try to login user with new password
        self.api(None, 'POST', self.prefix() + '/sessions', body={'username': 'user',
                                                                  'password': 'a'},
                 expected_code=http.status.CREATED,
                 expected_result_contain_keys={'id', 'token'})

    def test_admin_delete_user(self):
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/', expected_code=http.status.OK)
        self.assertTrue('summary' in self.last_result and 'total_items' in self.last_result['summary'] and \
                        self.last_result['summary']['total_items'] == 3)
        self.api(self.token_admin, 'DELETE', self.prefix() + f'/admin/{self.id_user}',
                 expected_code=http.status.NO_CONTENT)
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/', expected_code=http.status.OK)
        self.assertTrue('summary' in self.last_result and 'total_items' in self.last_result['summary'] and \
                        self.last_result['summary']['total_items'] == 2)

    def test_user_tries_to_delete_user(self):
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/', expected_code=http.status.OK)
        self.assertTrue('summary' in self.last_result and 'total_items' in self.last_result['summary'] and \
                        self.last_result['summary']['total_items'] == 3)
        self.api(self.token_user2, 'DELETE', self.prefix() + f'/admin/{self.id_user}',
                 expected_code=http.status.UNAUTHORIZED)
        self.api(self.token_admin, 'GET', self.prefix() + f'/admin/', expected_code=http.status.OK)
        self.assertTrue('summary' in self.last_result and 'total_items' in self.last_result['summary'] and \
                        self.last_result['summary']['total_items'] == 3)

    def test_user_reset_password_using_forgot_password_feature(self):
        # try to login with current password
        self.api(None, 'POST', self.prefix() + f'/sessions', body={'username': 'user2', 'password': THE_PASSWORD},
                 expected_code=http.status.CREATED)

        self.api(None, 'POST', self.prefix() + f'/forgot?username=user2', expected_code=http.status.NO_CONTENT)

        from base import store
        tmp_test_last_reset_password_id = store.get('tmp_test_last_reset_password_id').decode('ascii')

        self.api(None, 'POST', self.prefix() + f'/reset/{tmp_test_last_reset_password_id}', body={
            'password': THE_PASSWORD + '-new'
        })

        # try to login with an old password
        self.api(None, 'POST', self.prefix() + f'/sessions', body={'username': 'user2', 'password': THE_PASSWORD},
                 expected_code=http.status.UNAUTHORIZED)

        # login with a new password
        self.api(None, 'POST', self.prefix() + f'/sessions',
                 body={'username': 'user2', 'password': THE_PASSWORD + '-new'},
                 expected_code=http.status.CREATED)

        # try to reset password with an already used forgot code
        self.api(None, 'POST', self.prefix() + f'/reset/{tmp_test_last_reset_password_id}', body={
            'password': THE_PASSWORD + '-new2'},
                 expected_code=http.status.UNAUTHORIZED,
                 expected_result_subset={'id': 'FORGOT_PASSWORD_CODE_EXPIRED_OR_USED'})


if __name__ == '__main__':
    unittest.main()
