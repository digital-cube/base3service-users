# coding: utf8

import os
import sys
import unittest
import tornado.testing

_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(_root_dir)

from tests.test_register_users import TestUsersAbout
from tests.test_register_users import TestRegisterUsers
from tests.test_login_users import TestLoginUsers
from tests.test_tenants import TestTenants
from tests.test_users_scopes import TestUsersScopes
from tests.test_users import TestUsers
from tests.test_users import TestUser


def all():
    _tests = [
        TestUsersAbout, TestRegisterUsers, TestLoginUsers, TestTenants, TestUsersScopes, TestUsers, TestUser
    ]

    _loader = unittest.TestLoader()
    _tests = [_loader.loadTestsFromTestCase(t) for t in _tests]
    _all = unittest.TestSuite(_tests)
    return _all


if __name__ == '__main__':
    """
    Run all tests.
    Make sure the test database is created. For postgresql and mysql create database test_[configured database name]
    """

    tornado.testing.main()
