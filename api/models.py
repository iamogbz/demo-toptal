"""
Jogger api model definitions
"""
from django.db import models
from django.contrib.auth.models import (
    User,
    Permission,
)


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
            ("view_scope", "Can view scope"),
        )


class Account(User):
    """
    User account model
    """
    reset_code = models.TextField()

    class Meta:
        permissions = (
            ("view_account", "Can view account"),
            ("manage_account", "Can manage account"),
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
    scope = models.ManyToManyField(Scope)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        permissions = (
            ("view_auth", "Can view auth"),
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
            ("view_trip", "Can view trip"),
        )
