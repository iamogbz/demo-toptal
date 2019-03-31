"""
Api permissions module
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

from api import models, views


class JoggerPermissions(BasePermission):
    """
    Control permissions on user accounts accessing api
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        if isinstance(view, (views.AccountViewSet, views.TripViewSet)):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if isinstance(obj, models.Account):
            if user.id == obj.id:
                return True
            if user.id in obj.managers and request.method in SAFE_METHODS:
                return True
        if isinstance(obj, models.Trip):
            if user.id == obj.account.id:
                return True
            if user.id in obj.account.managers:
                return True
        return False
