"""
Define model serializers here
"""
from rest_framework.serializers import ModelSerializer

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
        fields = ('id', 'name', 'codename', 'includes')


class AuthSerializer(ModelSerializer):
    """
    Authentication details serializer
    """
    class Meta:
        model = Auth
        fields = ('id', 'token', 'user', 'owner',
                  'scopes', 'granted', 'date_created')


class AccountSerializer(ModelSerializer):
    """
    Account details serializer
    """
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class TripSerializer(ModelSerializer):
    """
    Trip session serializer
    """
    class Meta:
        model = Trip
        fields = '__all__'
