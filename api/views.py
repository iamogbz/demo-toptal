"""
Api app views
"""
from django.shortcuts import get_object_or_404
from rest_framework.decorators import (
    list_route,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.generics import GenericAPIView

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

    @list_route(methods=['GET', 'PUT'], url_path='profile')
    def profile(self, request, *args, **kwargs):
        """
        Handle showing and updating of tracking information
        """
        obj = get_object_or_404(Account, pk=request.user.id)
        if request.method == 'GET':
            obj = get_object_or_404(Account, pk=request.user.id)
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


class TripViewSet(ModelViewSet):
    """
    Control trip session model
    """
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
