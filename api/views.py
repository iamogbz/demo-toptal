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
from api.constants import Methods


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

    @list_route(methods=[Methods.GET, Methods.PUT])
    def profile(self, request, *_, **kwargs):
        """
        Handle showing and updating of tracking information
        """
        obj = get_object_or_404(models.Account, pk=request.user.id)
        if request.method == Methods.GET:
            obj = get_object_or_404(models.Account, pk=request.user.id)
            serializer = self.get_serializer(obj)
            response = Response(serializer.data)
        elif request.method == Methods.PUT:
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

    @list_route(methods=[Methods.GET, Methods.POST, Methods.DELETE])
    def managers(self, request, *_, **__):
        """
        Handle listing and adding accounts that can manage user
        """
        user = models.Account.objects.get(pk=request.user.id)
        method = request.method
        response_data = None
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        if method == Methods.GET:
            mgrs = models.Account.objects.filter(pk__in=user.managers)
            serializer = self.get_serializer(mgrs, many=True)
            response_data = serializer.data
            response_status = status.HTTP_200_OK
        elif method in [Methods.POST, Methods.DELETE]:
            mgr_email = request.data['email']
            # if email is not None or empty string
            if mgr_email:
                if user.email == mgr_email:
                    utils.raise_api_exc(
                        APIException('you are signed with this email'),
                        status.HTTP_400_BAD_REQUEST,
                    )

                # check if account email exists
                mgr = get_object_or_404(models.Account, email=mgr_email)
                if method == Methods.POST:
                    if _auth_manager(user=user, mgr=mgr):
                        response_data = self.get_serializer(mgr).data
                        response_status = status.HTTP_202_ACCEPTED
                elif _deauth_manager(user=user, mgr=mgr):
                    response_status = status.HTTP_204_NO_CONTENT
            else:
                utils.raise_api_exc(
                    APIException('no email supplied'),
                    status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=response_data,
            status=response_status,
        )


def _auth_manager(user, mgr):
    """
    Authorise and notify manager for user account
    :raises APIException: if manager already authorized
    """
    # check if account already manages current user
    if mgr.id in user.managers:
        utils.raise_api_exc(
            APIException('email already authorised'),
            status.HTTP_400_BAD_REQUEST
        )

    # get scope for managing user account
    mgr_scope = models.Scope.objects.get(
        codename=PermissionCodes.Account.MANAGE,
    )
    # get previous
    _deauth_manager(user=user, mgr=mgr)
    auth = models.Auth.objects.create(
        owner=mgr,
        user=user,
        active=False,
        code=get_random_string(128),
    )
    auth.scopes.set({mgr_scope})
    auth.save()
    # Send notice to account to complete authorisation
    # Only return True if auth created
    return True


def _deauth_manager(user, mgr):
    """
    Deauthorise manager on user account
    :raises APIException: if user was not authorised
    """
    # deauth all previous
    return models.Auth.objects.filter(owner=mgr, user=user).update(
        active=False, code=None,
    )


class TripViewSet(viewsets.ModelViewSet):
    """
    Control trip session model
    """
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
