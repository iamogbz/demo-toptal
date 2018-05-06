"""
Test permission module
"""
from unittest.mock import MagicMock
from django.test import SimpleTestCase

from api import (
    models,
    views,
)
from api.constants import Methods
from api.permissions import JoggerPermissions


class JoggerPermissionsTest(SimpleTestCase):
    """
    Test jogger permissions
    """

    def setUp(self):
        self.permissions = JoggerPermissions()

    def test_has_permission(self):
        """
        Test view level access
        """
        user = MagicMock()
        user.is_superuser = True
        request = MagicMock()
        request.user = user
        view = views.AuthViewSet()
        self.assertTrue(self.permissions.has_permission(request, view))
        request.user.is_superuser = False
        self.assertFalse(self.permissions.has_permission(request, view))
        view = views.AccountViewSet()
        self.assertTrue(self.permissions.has_permission(request, view))

    def test_has_object_permission(self):
        """
        Test object level access
        """
        _ = None
        user = MagicMock(spec=models.Account)
        user.id = 1
        user.is_superuser = True
        req = MagicMock()
        req.user = user
        self.assertTrue(self.permissions.has_object_permission(req, _, _))

        req.user.is_superuser = False
        acc = MagicMock(spec=models.Account)
        acc.id = 99
        acc.managers = {}
        self.assertFalse(self.permissions.has_object_permission(req, _, acc))
        req.user.id = acc.id
        self.assertTrue(self.permissions.has_object_permission(req, _, acc))

        req.user.id = 1
        acc.managers = {req.user.id}
        req.method = Methods.DELETE
        self.assertFalse(self.permissions.has_object_permission(req, _, acc))
        req.method = Methods.GET
        self.assertTrue(self.permissions.has_object_permission(req, _, acc))

        trip = MagicMock(spec=models.Trip)
        trip.account = MagicMock(spec=models.Account)
        self.assertFalse(self.permissions.has_object_permission(req, _, trip))
        trip.account.id = user.id
        self.assertTrue(self.permissions.has_object_permission(req, _, trip))
        trip.account = acc
        self.assertTrue(self.permissions.has_object_permission(req, _, trip))
