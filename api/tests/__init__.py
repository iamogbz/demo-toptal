"""
Test definitions in api module
"""
from django.test import TestCase
from rest_framework.exceptions import APIException

from api.constants import (
    Limits,
    Methods,
    PermissionCodes,
)
from api.utils import (
    has_required,
    raise_api_exc,
)


class ConstantsTest(TestCase):
    """
    Test values defined in constants.py
    """

    def test_account_manage_limits(self):
        """
        Test account manager limits in reasonable range
        """
        minimum = 1
        maximum = 50
        self.assertGreaterEqual(Limits.ACCOUNT_MANAGED, minimum)
        self.assertGreaterEqual(Limits.ACCOUNT_MANAGER, minimum)
        self.assertLessEqual(Limits.ACCOUNT_MANAGED, maximum)
        self.assertLessEqual(Limits.ACCOUNT_MANAGER, maximum)


class UtilsTest(TestCase):
    """
    Test utility functions
    """

    def test_has_required(self):
        """
        Test utils.has_required function
        """
        self.assertTrue(has_required({1, 2, 3, 4}, {2, 3}))
        self.assertFalse(has_required({1, 2, 3, 4}, {2, 3, 99}))

    def test_raise_api_exec(self):
        """
        Test utils.raise_api_exec function
        """
        status_code = 419
        with self.assertRaises(APIException):
            try:
                raise_api_exc(APIException(), status_code)
            except APIException as exc:
                self.assertEqual(exc.status_code, status_code)
                raise exc
