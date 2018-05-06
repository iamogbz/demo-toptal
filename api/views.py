"""
Api app views
"""
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
)
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api import (
    models,
    permissions,
    serializers,
    utils,
)
from api.constants import (
    MAIL_FROM,
    Limits,
    Methods,
    PermissionCodes,
    Templates,
)
from api.utils import send_mail


@api_view([Methods.POST])
@permission_classes([AllowAny])
def auth_user(request):
    """
    Authenticate user using email and password
    """
    data = request.data
    if utils.has_required(data.keys(), {'email', 'password'}):
        user = get_object_or_404(models.Account, email=data['email'])
        if user.check_password(data['password']):
            response = JsonResponse(serializers.AccountSerializer(user).data)
        else:
            utils.raise_api_exc(
                APIException('invalid credentials'),
                status.HTTP_400_BAD_REQUEST,
            )
    else:
        utils.raise_api_exc(
            APIException('incomplete information'),
            status.HTTP_400_BAD_REQUEST,
        )
    return response


@api_view([Methods.GET, Methods.POST])
@permission_classes([AllowAny])
def auth_reset(request):
    """
    Control user account password reset
    """
    if request.method == Methods.GET:
        email = request.query_params.get('email')
        if email:
            user = get_object_or_404(models.Account, email=email)
            reset_code = get_random_string(128)
            user.set_reset_code(reset_code, True)
            _send_reset_request_mail(request, user, reset_code)
            response = Response(data={
                'detail': 'reset code has been sent to your email',
            }, status=status.HTTP_200_OK)
        else:
            utils.raise_api_exc(
                APIException('email is required to request a reset'),
                status.HTTP_400_BAD_REQUEST,
            )
    else:
        # POST
        data = request.data
        if utils.has_required(data.keys(), {'email', 'code', 'password'}):
            user = get_object_or_404(models.Account, email=data['email'])
            if user.check_reset_code(data['code']):
                user.set_password(data['password'])
                user.clear_reset_code()
                user.save()
                _send_reset_confirm_mail(request, user)
                response = Response(data={
                    'detail': 'password reset successfully',
                }, status=status.HTTP_200_OK)
            else:
                utils.raise_api_exc(
                    APIException('invalid reset code'),
                    status.HTTP_400_BAD_REQUEST,
                )
        else:
            utils.raise_api_exc(
                APIException('incomplete reset details'),
                status.HTTP_400_BAD_REQUEST,
            )
    return response


def _send_reset_request_mail(request, user, code):
    """
    Send password reset request mail
    :param request: request context
    :param user: user account
    :param code: reset code
    """
    reset_link = '{}?code={}'.format(
        request.build_absolute_uri(reverse('auth-reset')),
        code,
    )
    send_mail(
        sender=MAIL_FROM,
        recievers=[user.email],
        subject='Account Password Reset',
        tmpl_file=Templates.Email.RESET_REQUEST,
        tmpl_data={
            '{email}': user.email,
            '{reset_confirm_link}': reset_link,
        },
    )


def _send_reset_confirm_mail(_, user):
    """
    Send confirmation of password reset change
    """
    send_mail(
        sender=MAIL_FROM,
        recievers=[user.email],
        subject='Account Password Changed',
        tmpl_file=Templates.Email.RESET_COMPLETE,
        tmpl_data={},
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
        if self.action == 'trips':
            return serializers.TripSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        acc = get_object_or_404(models.Account, pk=self.request.user.id)
        if acc.is_superuser:
            return self.queryset
        return self.queryset.filter(pk=acc.id)

    @action(
        methods=[Methods.GET, Methods.PUT, Methods.PATCH, Methods.DELETE],
        detail=False,
    )
    def profile(self, request, *_, **kwargs):
        """
        Handle showing, updating and deletion of account
        """
        obj = get_object_or_404(models.Account, pk=request.user.id)
        if request.method == Methods.GET:
            obj = get_object_or_404(models.Account, pk=request.user.id)
            serializer = self.get_serializer(obj)
            response = Response(serializer.data)
        elif request.method in [Methods.PUT, Methods.PATCH]:
            partial = kwargs.pop('partial', request.method == Methods.PATCH)
            serializer = self.get_serializer(
                obj,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            response = Response(serializer.data)
        else:
            # DELETE
            obj.delete()
            response = Response(
                data=None,
                status=status.HTTP_204_NO_CONTENT,
            )
        return response

    @action(
        methods=[Methods.GET, Methods.POST], detail=False,
        url_path='(?P<user_id>[0-9]+)/trips',
    )
    def trips(self, request, user_id):
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
            trips = self.paginate_queryset(acc.trips.all())
            serializer = self.get_serializer(
                trips, many=True, context={'request': request})
            response = self.get_paginated_response(serializer.data)
        else:
            # POST
            result = create_trip(acc, request.data.copy(), request)
            if result.errors:
                response = Response(
                    result.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = Response(
                    result.data, status=status.HTTP_201_CREATED)
        return response

    @action(methods=[Methods.GET, Methods.POST, Methods.DELETE], detail=False)
    def managers(self, request):
        """
        Handle listing and adding accounts that can manage user
        """
        user = get_object_or_404(models.Account, pk=request.user.id)
        method = request.method
        response_data = None
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        if method == Methods.GET:
            mgrs = models.Account.objects.filter(pk__in=user.managers)
            serializer = self.get_serializer(mgrs, many=True)
            response_data = serializer.data
            response_status = status.HTTP_200_OK
        else:
            # POST & DELETE
            if utils.has_required(request.data.keys(), {'email'}):
                mgr_email = request.data['email']
                if user.email == mgr_email:
                    utils.raise_api_exc(
                        APIException('you are signed with this email'),
                        status.HTTP_400_BAD_REQUEST,
                    )
                mgr = get_object_or_404(models.Account, email=mgr_email)
                if method == Methods.POST:
                    auth = auth_manager(user=user, mgr=mgr)
                    self._send_manage_request_mail(user, mgr_email, auth)
                    response_data = self.get_serializer(mgr).data
                    response_status = status.HTTP_202_ACCEPTED
                else:
                    # DELETE
                    deauth_manager(user=user, mgr=mgr)
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

    def _send_manage_request_mail(self, user, mgr_email, auth):
        """
        Send mail to manager requested for confirmation
        """
        confirm_link = '{}?code={}'.format(
            self.request.build_absolute_uri(
                reverse('account-managing')),
            auth.code,
        )
        send_mail(
            sender=MAIL_FROM,
            recievers=[mgr_email],
            subject='Account Manage Request',
            tmpl_file=Templates.Email.MANAGE_REQUEST,
            tmpl_data={
                '{username}': user.username,
                '{user_email}': user.email,
                '{manager_email}': mgr_email,
                '{manage_confirm_link}': confirm_link,
            },
        )
        cancel_link = '{}?email={}'.format(
            self.request.build_absolute_uri(
                reverse('account-managers')),
            mgr_email,
        )
        send_mail(
            sender=MAIL_FROM,
            recievers=[user.email],
            subject='Account Manager Request',
            tmpl_file=Templates.Email.MANAGER_REQUEST,
            tmpl_data={
                '{manager_email}': mgr_email,
                '{manage_cancel_link}': cancel_link,
            },
        )

    @action(methods=[Methods.GET, Methods.POST, Methods.DELETE], detail=False)
    def managing(self, request):
        """
        Handle listing and updating account user is currently managing
        """
        mgr = get_object_or_404(models.Account, pk=request.user.id)
        method = request.method
        response_data = None
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        if method == Methods.GET:
            mngn = models.Account.objects.filter(pk__in=mgr.managing)
            serializer = self.get_serializer(mngn, many=True)
            response_data = serializer.data
            response_status = status.HTTP_200_OK
        elif method == Methods.POST:
            if utils.has_required(request.data.keys(), {'code'}):
                auth_code = request.data['code']
                auth = get_object_or_404(
                    models.Auth, code=auth_code, owner_id=mgr.id)
                auth.activate()
                response_data = self.get_serializer(auth.user).data
                response_status = status.HTTP_200_OK
            else:
                utils.raise_api_exc(
                    APIException('no authorization code supplied'),
                    status.HTTP_400_BAD_REQUEST,
                )
        else:
            # DELETE
            if utils.has_required(request.data.keys(), {'email'}):
                usr_email = request.data['email']
                user = get_object_or_404(models.Account, email=usr_email)
                deauth_manager(user=user, mgr=mgr)
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


def auth_manager(user, mgr):
    """
    Authorise and notify manager for user account
    :raises APIException: if manager already authorized
    :raises APIException: if manager managing at limit
    :raises APIException: if user manager count at limit
    """
    if mgr.id in user.managers:
        utils.raise_api_exc(
            APIException('email already authorised'),
            status.HTTP_400_BAD_REQUEST
        )
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

    mgr_scope = models.Scope.objects.get(
        codename=PermissionCodes.Account.MANAGE,
    )
    deauth_manager(user=user, mgr=mgr)
    auth = models.Auth.objects.create(
        owner=mgr,
        user=user,
        active=False,
        code=get_random_string(128),
    )
    auth.scopes.set({mgr_scope})
    auth.save()
    return auth


def deauth_manager(user, mgr):
    """
    Deauthorise all manager auth on user account
    """
    return models.Account.get_manage_scope().auths.filter(
        user=user, owner=mgr,
    ).update(
        active=False, code=None,
    )


class TripViewSet(viewsets.ModelViewSet):
    """
    Control trip session model on all accounts
    """
    queryset = models.Trip.objects.all()
    serializer_class = serializers.TripSerializer
    permission_classes = (
        permissions.JoggerPermissions,
    )

    def create(self, request, *_, **__):
        result = create_trip(request.user, request.data.copy(), request)
        if result.errors:
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(result.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        acc = get_object_or_404(models.Account, pk=self.request.user.id)
        if acc.is_superuser:
            return self.queryset
        return self.queryset.filter(account_id__in=({acc.id} | acc.managing))


def create_trip(account, data, request=None):
    """
    Create trip on account using data
    """
    for k in ['account', 'account_id']:
        if k in data:
            del data[k]
    data['account'] = account
    setattr(request, 'user', account)
    serializer = serializers.TripSerializer(
        data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
    return serializer
