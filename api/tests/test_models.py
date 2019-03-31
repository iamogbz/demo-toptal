"""
Test api models
"""
from django.test import TestCase
from django.utils.crypto import get_random_string

from api.constants import PermissionCodes
from api.models import Scope, Permission, Auth, Account, Trip
from api.tests import FixturesMixin, AccountMixin


class ScopeTest(FixturesMixin, TestCase):
    """
    Test model definitions
    """

    def test_scope_description(self):
        """
        Test scope description is permission name
        """
        scope = Scope.objects.first()
        self.assertEqual(
            Scope.objects.first().description, Permission.objects.get(pk=scope.id).name
        )


class AuthTest(AccountMixin, TestCase):
    """
    Test auth model
    """

    def test_auth_activate(self):
        """
        Test that auth can be activated only once
        """
        auth = Auth.objects.create(user_id=3, owner_id=2, code=get_random_string(16))
        self.assertFalse(auth.active)
        self.assertIsNotNone(auth.code)

        auth.activate()
        auth.refresh_from_db()
        self.assertTrue(auth.active)
        self.assertIsNone(auth.code)

        auth.deactivate()
        auth.refresh_from_db()
        self.assertFalse(auth.active)
        self.assertIsNone(auth.code)

        auth.activate()
        auth.refresh_from_db()
        self.assertFalse(auth.active)
        self.assertIsNone(auth.code)

    def test_scopes_flatten_invalid(self):
        """
        Test auth scope flatten function
        """
        implicit = [PermissionCodes.Account.MANAGE, PermissionCodes.Account.CREATE]
        explicit = implicit.copy()
        explicit.extend(
            [
                PermissionCodes.Account.VIEW,
                PermissionCodes.Trip.VIEW,
                PermissionCodes.Trip.CREATE,
                PermissionCodes.Trip.EDIT,
                PermissionCodes.Trip.DELETE,
            ]
        )
        implicit_ids = [Scope.objects.get(codename=scope).id for scope in implicit]
        explicit_ids = {Scope.objects.get(codename=scope).id for scope in explicit}
        pancake = Auth.flatten_scopes([0, 420] + implicit_ids)
        self.assertSetEqual(pancake, explicit_ids)

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


class AccountTest(AccountMixin, TestCase):
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
            account=account, length_time=trip_time, length_distance=trip_distance
        )
        self.assertEqual(trip.date_created, trip.date_updated)
