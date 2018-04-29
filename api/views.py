"""
Api app views
"""
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import list_route
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api import (
    models,
    permissions,
    serializers,
    utils,
)
from api.constants import PermissionCodes


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
    permission_classes = (
        permissions.JoggerPermissions,
    )

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

    @list_route(methods=['GET', 'POST'])
    def managers(self, request, *_, **__):
        """
        Handle listing and adding accounts that can manage user
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user.managers, many=True)
            response = Response(serializer.data)
        elif request.method == 'POST':
            account_email = request.data['email']
            # if email is not None or empty string
            if account_email:
                if user.email == account_email:
                    utils.raise_api_exc(
                        APIException('you are signed with this email'),
                        status.HTTP_400_BAD_REQUEST,
                    )

                # check if account email exists
                owner = models.Account.objects.get_object_or_404(
                    email=account_email
                )
                # check if account already manages current user
                if owner.id in user.managers:
                    utils.raise_api_exc(
                        APIException('email already authorised'),
                        status.HTTP_400_BAD_REQUEST
                    )

                # get scope for managing user account
                mgr_scope = models.Scope.objects.get(
                    codename=PermissionCodes.Account.MANAGE,
                )
                # get previous
                auth, _ = models.Auth.objects.get_or_create(
                    owner=owner,
                    user=user,
                    scopes=[mgr_scope],
                    active=False,
                    defaults={
                        'code': get_random_string(128),
                    },
                )
                # TODO send notice to account to complete authorisation
                response = Response(
                    data=self.get_serializer(owner),
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                utils.raise_api_exc(
                    APIException('no email supplied'),
                    status.HTTP_400_BAD_REQUEST,
                )

        return response


class TripViewSet(viewsets.ModelViewSet):
    """
    Control trip session model
    """
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
