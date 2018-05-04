"""
Test api models
"""
from django.test import TestCase
from django.utils.crypto import get_random_string

from api.constants import PermissionCodes
from api.models import (
    Scope,
    Permission,
    Auth,
    Account,
    Trip,
)
from api.tests import FixturesMixin


class ScopeTest(FixturesMixin, TestCase):
    """
    Test model definitions
    """

    def test_scope_description(self):
        """
        Test scope description is permission name
        """
        self.assertEqual(
            Scope.objects.get(pk=19).description,
            Permission.objects.get(pk=19).name,
        )


class AuthTest(FixturesMixin, TestCase):
    """
    Test auth model
    """

    def test_scope_granted_includes(self):
        """
        Test that granted property of auth includes nested scopes
        """
        auth = Auth.objects.get(pk=1)
        mgscope = Scope.objects.get(codename=PermissionCodes.Account.MANAGE)
        vwscope = Scope.objects.get(codename=PermissionCodes.Account.VIEW)
        self.assertIn(mgscope, auth.scopes.all())
        self.assertNotIn(vwscope, auth.scopes.all())
        self.assertIn(vwscope.id, auth.granted)


class AccountTest(FixturesMixin, TestCase):
    """
    Test account model
    """

    def test_account_reset(self):
        """
        Test setting and checking account reset code
        """
        plain_code = get_random_string(16)
        account = Account.objects.get(pk=3)
        self.assertFalse(account.check_reset_code(plain_code))
        account.set_reset_code(plain_code)
        self.assertNotEqual(account.reset_code, plain_code)
        self.assertTrue(account.check_reset_code(plain_code))

    def test_account_manage_property(self):
        """
        Test account model manage properties get correctly populated
        """
        account = Account.objects.get(pk=3)
        managers = {2}
        self.assertEqual(managers, account.managers)
        account = Account.objects.get(pk=2)
        managing = {3}
        self.assertEqual(managing, account.managing)


class TripTest(FixturesMixin, TestCase):
    """
    Test trip model
    """

    def test_trip_creation(self):
        """
        Test building and saving of trip object
        """
        account = Account.objects.get(pk=3)
        trip_time = 1800
        trip_distance = 10000
        trip = Trip.objects.create(
            account=account,
            length_time=trip_time,
            length_distance=trip_distance,
        )
        self.assertEqual(trip.date_created, trip.date_updated)
