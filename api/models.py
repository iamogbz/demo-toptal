"""
Jogger api model definitions
"""
from django.db import models
from django.contrib.auth.models import (
    User,
    Permission,
)
from api.constants import PermissionCodes


class Scope(Permission):
    """
    Authorisation scopes
    """
    @property
    def description(self):
        """
        Use description to access name property
        """
        return self.name

    includes = models.ManyToManyField("self", symmetrical=False, blank=True)

    class Meta:
        permissions = (
            (PermissionCodes.Scope.VIEW, "Can view scope"),
        )


class Account(User):
    """
    User account model
    """
    reset_code = models.TextField(null=True)

    class Meta:
        permissions = (
            (PermissionCodes.Account.VIEW, "Can view account"),
            (PermissionCodes.Account.MANAGE, "Can manage account"),
        )


class Auth(models.Model):
    """
    Custom authorisation class
    """
    user = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="user",
    )
    owner = models.ForeignKey(
        Account,
        null=True,
        on_delete=models.SET_NULL,
        related_name="owner",
    )
    token = models.TextField()
    code = models.TextField(null=True)
    scopes = models.ManyToManyField(Scope)
    date_created = models.DateField(auto_now_add=True)

    @property
    def granted(self):
        """
        All scopes implicitly granted to this authorisation
        """
        return Auth.flatten_scopes(self.scopes.values_list('id', flat=True))

    @staticmethod
    def flatten_scopes(scope_ids):
        """
        Take list of scope ids and flatten includes
        into single set of implicit scope permissions
        """
        pancake = set()
        queue = set(scope_ids)
        while queue:
            sid = queue.pop()
            if sid not in pancake:
                try:
                    scope = Scope.objects.get(pk=sid)
                    pancake.add(sid)
                    queue.update(scope.includes.values_list('id', flat=True))
                except Scope.DoesNotExist:
                    pass
        return pancake

    class Meta:
        permissions = (
            (PermissionCodes.Auth.VIEW, "Can view auth"),
        )


class Trip(models.Model):
    """
    An exercise session model
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    length_time = models.PositiveIntegerField()
    length_distance = models.PositiveIntegerField()
    date_updated = models.DateField(auto_now=True)

    class Meta:
        permissions = (
            (PermissionCodes.Trip.VIEW, "Can view trip"),
        )
