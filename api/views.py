"""
Api app views
"""
from rest_framework.viewsets import ModelViewSet

from api.models import (
    Account,
    Auth,
    Trip,
    Scope,
)
from api.serializers import (
    AccountSerializer,
    AuthSerializer,
    TripSerializer,
    ScopeSerializer,
)


class ScopeViewSet(ModelViewSet):
    """
    Control auth scope model
    """
    queryset = Scope.objects.all()
    serializer_class = ScopeSerializer


class AuthViewSet(ModelViewSet):
    """
    Control auth model
    """
    queryset = Auth.objects.all()
    serializer_class = AuthSerializer


class AccountViewSet(ModelViewSet):
    """
    Control account model
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TripViewSet(ModelViewSet):
    """
    Control trip session model
    """
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
