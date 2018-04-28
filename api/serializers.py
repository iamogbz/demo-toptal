"""
Define model serializers here
"""
from rest_framework import serializers

from api import models


class ScopeSerializer(serializers.ModelSerializer):
    """
    Authorisation scope serializer
    """

    class Meta:
        model = models.Scope
        fields = ('id', 'name', 'codename', 'includes')


class AuthSerializer(serializers.ModelSerializer):
    """
    Authentication details serializer
    """
    class Meta:
        model = models.Auth
        fields = (
            'id',
            'token', 'code',
            'user', 'owner',
            'scopes', 'granted',
            'active', 'date_created',
        )


class AccountSerializer(serializers.ModelSerializer):
    """
    Account details serializer
    """
    class Meta:
        model = models.Account
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class TripSerializer(serializers.ModelSerializer):
    """
    Trip session serializer
    """
    class Meta:
        model = models.Trip
        fields = '__all__'
