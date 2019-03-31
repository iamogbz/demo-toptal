"""
Test definitions in api module
"""
from api.models import Account


class FixturesMixin:
    """
    Fixture test to load data
    """

    fixtures = ["initial_data_api.json"]


class AccountMixin(FixturesMixin):
    """
    Mixin with superuser loaded
    """

    superuser = Account.objects.get(pk=1)
    user = Account.objects.get(pk=3)
    mgr = Account.objects.get(pk=2)
