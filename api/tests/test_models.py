"""
Test api models
"""
from django.test import TestCase

from api.constants import PermissionCodes
from api.models import (
    Scope,
    Permission,
    Auth,
    Account,
    User,
    Trip,
)


class FixturesMixin(object):
    """
    Fixture test to load data
    """
    fixtures = [
        'initial_data_api.json',
    ]


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
    pass


class TripTest(FixturesMixin, TestCase):
    """
    Test trip model
    """
    pass
