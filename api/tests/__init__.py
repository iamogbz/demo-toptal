"""
Test definitions in api module
"""
from api.constants import PermissionCodes
from api.models import Account, Auth, Scope


class FixturesMixin:
    """
    Fixture test to load data
    """

    fixtures = ["initial_data_api.json"]

    def setUp(self):
        Scope.create_all()


class AccountMixin(FixturesMixin):
    """
    Mixin with superuser loaded
    """

    superuser = Account.objects.get(pk=1)
    user = Account.objects.get(pk=3)
    mgr = Account.objects.get(pk=2)

    def setUp(self):
        super().setUp()
        manage_scope = Scope.objects.get(codename=PermissionCodes.Account.MANAGE)
        for i in range(3):
            auth_obj = Auth.objects.create(user=self.user, owner=self.mgr)
            auth_obj.active = i == 0
            auth_obj.scopes.set([manage_scope])
            auth_obj.save()
