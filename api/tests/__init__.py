"""
Test definitions in api module
"""
from api.constants import PermissionCodes
from api.models import Account, Auth, Scope


class FixturesMixin:
    """
    Fixture test to load data
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Scope.create_all()

    fixtures = ["initial_data_api.json"]


class AccountMixin(FixturesMixin):
    """
    Mixin with superuser loaded
    """

    superuser = Account.objects.get(pk=1)
    user = Account.objects.get(pk=3)
    mgr = Account.objects.get(pk=2)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        manage_scope = Scope.object.get(codename=PermissionCodes.Account.MANAGE)
        Auth.objects.create(user=3, owner=2, scopes=[manage_scope])
        Auth.objects.create(user=3, owner=2, scopes=[manage_scope])
        Auth.objects.create(user=3, owner=2, scopes=[manage_scope], active=True)
