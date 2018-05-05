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
            'id', 'code',
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
    owner = serializers.ReadOnlyField(source='account_id')

    def create(self, validated_data):
        request = self.context['request']
        for k in ['account', 'account_id']:
            if k in validated_data:
                del validated_data[k]
        validated_data['account_id'] = request.user.id
        return models.Trip.objects.create(**validated_data)

    class Meta:
        model = models.Trip
        fields = (
            'id', 'owner', 'date_created',
            'length_distance', 'length_time',
        )
