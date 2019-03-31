"""
Jogger api model definitions
"""
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User, Permission
from django.core.validators import MinValueValidator
from django.db import models

from api.constants import PermissionCodes


class Scope(Permission):
    """
    Authorisation scopes
    """

    @classmethod
    def create_all(cls):
        """
        Create all scopes from permission codes
        """
        permission_classes = [
            PermissionCodes.Account,
            PermissionCodes.Auth,
            PermissionCodes.Scope,
            PermissionCodes.Trip,
        ]
        permission_attrs = ["CREATE", "VIEW", "EDIT", "DELETE", "MANAGE"]
        for permission_cls in permission_classes:
            cls_dict = vars(permission_cls)
            for attr in permission_attrs:
                permission_code = cls_dict.get(attr)
                if not permission_code:
                    continue
                permission = Permission.objects.get(codename=permission_code)
                cls(permission_ptr=permission).save_base(raw=True)

    @property
    def description(self):
        """
        Use description to access name property
        """
        return self.name

    @property
    def includes(self):
        """
        Get all scopes that this implicitly includes
        """
        return Scope.objects.filter(
            codename__in=PermissionCodes.graph.get(self.codename, [])
        )


class Account(User):
    """
    User account model
    """

    reset_code = models.TextField(null=True)

    def set_reset_code(self, plain_code, save=False):
        """
        Set account reset code
        :param plain_code: plain text code to encode
        :param save: flag controlling auto commit
        """
        self.reset_code = make_password(plain_code)
        if save:
            self.save()

    def check_reset_code(self, plain_code):
        """
        Check account reset code
        :param plain_code: the plain text reset code to check
        :returns bool: True if the reset code match
        """
        return check_password(plain_code, self.reset_code or "")

    def clear_reset_code(self, save=False):
        """
        Set the account reset code to None
        """
        self.reset_code = None
        if save:
            self.save()

    @staticmethod
    def get_manage_scope():
        """
        Scope used for managing user accounts
        """
        return Scope.objects.get(codename=PermissionCodes.Account.MANAGE)

    @property
    def managers(self):
        """
        List of accounts managing this user
        """
        mgr_scope = self.get_manage_scope()
        return {
            auth.owner.id for auth in mgr_scope.auths.filter(user=self, active=True)
        }

    @property
    def managing(self):
        """
        List of accounts this user manages
        """
        mgr_scope = self.get_manage_scope()
        return {
            auth.user.id for auth in mgr_scope.auths.filter(owner=self, active=True)
        }

    class Meta:
        permissions = ((PermissionCodes.Account.MANAGE, "Can manage account"),)


class Auth(models.Model):
    """
    Custom authorisation class
    :property user: Account authorisation is granting access
    :property owner: Account this authorithy is granted to
    """

    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="authorised"
    )
    owner = models.ForeignKey(
        Account, null=True, on_delete=models.SET_NULL, related_name="authorities"
    )
    code = models.TextField(null=True)
    active = models.BooleanField(default=False)
    scopes = models.ManyToManyField(Scope, related_name="auths")
    date_created = models.DateField(auto_now_add=True)

    @property
    def granted(self):
        """
        All scopes implicitly granted to this authorisation
        """
        return Auth.flatten_scopes(self.scopes.values_list("id", flat=True))

    def activate(self):
        """
        Activate authorisation
        Only works if code is not falsy
        """
        if self.code:
            self.code = None
            self.active = True
            self.save(update_fields=["code", "active"])

    def deactivate(self):
        """
        Deactivate authorisation
        """
        self.code = None
        self.active = False
        self.save(update_fields=["code", "active"])

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
                    queue.update(scope.includes.values_list("id", flat=True))
                except Scope.DoesNotExist:
                    pass
        return pancake


class Trip(models.Model):
    """
    An exercise session model
    :param account: user account
    :param date_created: timestamp of date trip added
    :param length_time: total time of trip in seconds
    :param length_distance: total distance of trip in metres
    :param date_updated: timestamp of last edit made
    """

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trips")
    date_created = models.DateField(auto_now_add=True)
    length_time = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    length_distance = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    date_updated = models.DateField(auto_now=True)
