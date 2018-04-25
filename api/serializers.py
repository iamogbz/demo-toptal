"""
Define model serializers here
"""
from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    ModelSerializer,
)

from api.models import (
    Account,
    Auth,
    Trip,
    Scope,
)


class ScopeSerializer(ModelSerializer):
    """
    Authorisation scope serializer
    """

    class Meta:
        model = Scope
        fields = '__all__'


class AuthSerializer(ModelSerializer):
    """
    Authentication details serializer
    """
    class Meta:
        model = Auth
        fields = '__all__'


class AccountSerializer(ModelSerializer):
    """
    Account details serializer
    """
    class Meta:
        model = Account
        fields = '__all__'


class TripSerializer(ModelSerializer):
    """
    Trip session serializer
    """
    class Meta:
        model = Trip
        fields = '__all__'
