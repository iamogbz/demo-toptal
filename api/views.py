"""
Api app views
"""
from django.shortcuts import get_object_or_404
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import viewsets

from api import models
from api import serializers


class ScopeViewSet(viewsets.ModelViewSet):
    """
    Control auth scope model
    """
    queryset = models.Scope.objects.all()
    serializer_class = serializers.ScopeSerializer


class AuthViewSet(viewsets.ModelViewSet):
    """
    Control auth model
    """
    queryset = models.Auth.objects.all()
    serializer_class = serializers.AuthSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    Control account model
    """
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

    @list_route(methods=['GET', 'PUT'])
    def profile(self, request, *_, **kwargs):
        """
        Handle showing and updating of tracking information
        """
        obj = get_object_or_404(models.Account, pk=request.user.id)
        if request.method == 'GET':
            obj = get_object_or_404(models.Account, pk=request.user.id)
            serializer = self.get_serializer(obj)
            response = Response(serializer.data)
        elif request.method == 'PUT':
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                obj,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response = Response(serializer.data)

        return response


class TripViewSet(viewsets.ModelViewSet):
    """
    Control trip session model
    """
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
