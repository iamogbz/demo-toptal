"""
Api app views
"""
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from api import (
    models,
    permissions,
    serializers,
    utils,
)
from api.constants import (
    Limits,
    Methods,
    PermissionCodes,
)


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
    permission_classes = (
        permissions.JoggerPermissions,
    )


class AccountViewSet(viewsets.ModelViewSet):
    """
    Control account model
    """
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    permission_classes = (
        permissions.JoggerPermissions,
    )

    def get_serializer_class(self):
        if self.action == 'managed_trips':
            return serializers.TripSerializer
        return super().get_serializer_class()

    @action(methods=[Methods.GET, Methods.PUT], detail=False)
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

    @action(methods=[Methods.GET, Methods.POST], detail=False,
            url_path='(?P<user_id>[0-9]+)/trips')
    def managed_trips(self, request, user_id):
        """
        Handle viewing and adding of managed user jogging sessions
        """
        mgr = request.user
        acc = get_object_or_404(models.Account, pk=user_id)
        if all([
                mgr.id != acc.id,
                not mgr.is_superuser,
                mgr.id not in acc.managers,
        ]):
            raise Http404()
        if request.method == 'GET':
            trips = self.paginate_queryset(
                models.Trip.objects.filter(account_id=acc.id))
            serializer = self.get_serializer(
                trips, many=True, context={'request': request})
            response = self.get_paginated_response(serializer.data)
        else:
            result = create_trip(acc, request.data.copy(), request)
            if result.data:
                response = Response(result.data,
                                    status=status.HTTP_201_CREATED)
            else:
                response = Response(result.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
        return response

    @action(methods=[Methods.GET, Methods.POST, Methods.DELETE], detail=False)
    def managers(self, request):
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
            if mgr_email:
                if user.email == mgr_email:
                    utils.raise_api_exc(
                        APIException('you are signed with this email'),
                        status.HTTP_400_BAD_REQUEST,
                    )
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

    @action(methods=[Methods.GET, Methods.POST, Methods.DELETE], detail=False)
    def managing(self, request):
        """
        Handle listing and updating account user is currently managing
        """
        mgr = models.Account.objects.get(pk=request.user.id)
        method = request.method
        response_data = None
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        if method == Methods.GET:
            mngn = models.Account.objects.filter(pk__in=mgr.managing)
            serializer = self.get_serializer(mngn, many=True)
            response_data = serializer.data
            response_status = status.HTTP_200_OK
        elif method == Methods.POST:
            auth_code = request.data['code']
            if auth_code:
                auth = get_object_or_404(
                    models.Auth, code=auth_code, owner_id=mgr.id)
                auth.code = None
                auth.active = True
                auth.save(update_fields=['code', 'active'])
                response_data = self.get_serializer(auth.user).data
                response_status = status.HTTP_200_OK
            else:
                utils.raise_api_exc(
                    APIException('no authorization code supplied'),
                    status.HTTP_400_BAD_REQUEST,
                )
        elif method == Methods.DELETE:
            usr_email = request.data['email']
            if usr_email:
                if mgr.email == usr_email:
                    utils.raise_api_exc(
                        APIException('you are signed with this email'),
                        status.HTTP_400_BAD_REQUEST,
                    )
                user = get_object_or_404(models.Account, email=usr_email)
                if _deauth_manager(user=user, mgr=mgr):
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
    # check if above limit:
    if len(mgr.managing) >= Limits.ACCOUNT_MANAGED:
        utils.raise_api_exc(
            APIException('account is managing more than enough'),
            status.HTTP_406_NOT_ACCEPTABLE
        )
    if len(user.managers) >= Limits.ACCOUNT_MANAGER:
        utils.raise_api_exc(
            APIException('account has more than enough managers'),
            status.HTTP_406_NOT_ACCEPTABLE
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
    Deauthorise all manager auth on user account
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
    permission_classes = (
        permissions.JoggerPermissions,
    )

    def create(self, request, *_, **___):
        result = create_trip(request.user, request.data.copy(), request)
        if result.data:
            return Response(result.data, status=status.HTTP_201_CREATED)
        return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return models.Trip.objects.filter(account_id=self.request.user.id)


def create_trip(account, data, request=None):
    """
    Create trip on account using data
    """
    for k in ['account', 'account_id']:
        if k in data:
            del data[k]
    data['account'] = account
    serializer = serializers.TripSerializer(
        data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return serializer
    return None
