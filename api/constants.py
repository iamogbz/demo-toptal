"""
Api constants
"""
import os

from django.conf import settings

MAIL_HOST = os.getenv('SMTP_HOST')
MAIL_FROM = '{}@{}'.format(MAIL_HOST, os.getenv('SMTP_USER'))
MAIL_PORT = int(os.getenv('SMTP_PORT'))


class Limits:
    """
    Api limits
    """
    # limit to managers
    ACCOUNT_MANAGER = 5
    # limit to managing
    ACCOUNT_MANAGED = 25


class Methods:
    """
    Http method strings
    """
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class PermissionCodes:
    """
    All permission
    """
    class Account:
        """
        Account permissions
        """
        VIEW = 'view_account'
        EDIT = 'change_account'
        CREATE = 'create_account'
        DELETE = 'delete_account'
        MANAGE = 'manage_account'

    class Auth:
        """
        Authorisation permissions
        """
        VIEW = 'view_auth'
        EDIT = 'change_auth'
        CREATE = 'create_auth'
        DELETE = 'delete_auth'

    class Scope:
        """
        Scope permissions
        """
        VIEW = 'view_scope'
        EDIT = 'change_scope'
        CREATE = 'create_scope'
        DELETE = 'delete_scope'

    class Trip:
        """
        Trip permissions
        """
        VIEW = 'view_trip'
        EDIT = 'change_trip'
        CREATE = 'create_trip'
        DELETE = 'delete_trip'


class Templates:
    """
    Template files
    """
    class Email:
        """
        Email template paths
        """
        _ROOT = settings.BASE_DIR + '/api/static/email/'
        RESET_REQUEST = _ROOT + 'account_reset_request.tmpl'
        RESET_COMPLETE = _ROOT + 'account_reset_complete.tmpl'
        MANAGER_REQUEST = _ROOT + 'account_manager_request.tmpl'
        MANAGE_REQUEST = _ROOT + 'account_manage_request.tmpl'
