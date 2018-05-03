"""
Test definitions in api module
"""
from django.test import TestCase

from api.constants import (
    Limits,
    Methods,
    PermissionCodes,
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
