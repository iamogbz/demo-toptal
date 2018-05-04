"""
Test values defined in constants module
"""
from django.test import SimpleTestCase

from api.constants import (
    Limits,
)


class ConstantsTest(SimpleTestCase):
    """
    Test constants
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
