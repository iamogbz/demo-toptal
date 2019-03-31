"""
Api constants
"""
from django.conf import settings

from jogger.settings import SMTP_HOST, SMTP_PORT, SMTP_USER

MAIL_HOST = SMTP_HOST
MAIL_FROM = "{}@{}".format(MAIL_HOST, SMTP_USER)
MAIL_PORT = SMTP_PORT


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

    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


class PermissionCodes:
    """
    All permission
    """

    class Account:
        """
        Account permissions
        """

        VIEW = "view_account"
        EDIT = "change_account"
        CREATE = "add_account"
        DELETE = "delete_account"
        MANAGE = "manage_account"

    class Auth:
        """
        Authorisation permissions
        """

        VIEW = "view_auth"
        EDIT = "change_auth"
        CREATE = "add_auth"
        DELETE = "delete_auth"

    class Scope:
        """
        Scope permissions
        """

        VIEW = "view_scope"
        EDIT = "change_scope"
        CREATE = "add_scope"
        DELETE = "delete_scope"

    class Trip:
        """
        Trip permissions
        """

        VIEW = "view_trip"
        EDIT = "change_trip"
        CREATE = "add_trip"
        DELETE = "delete_trip"

    graph = {
        Account.MANAGE: [Account.VIEW, Trip.CREATE, Trip.EDIT, Trip.DELETE],
        Auth.EDIT: [Auth.VIEW],
        Auth.DELETE: [Auth.VIEW],
        Trip.EDIT: [Trip.VIEW],
        Trip.DELETE: [Trip.VIEW],
    }


class Templates:
    """
    Template files
    """

    class Email:
        """
        Email template paths
        """

        _ROOT = settings.BASE_DIR + "/api/static/email/"
        RESET_REQUEST = _ROOT + "account_reset_request.tmpl"
        RESET_COMPLETE = _ROOT + "account_reset_complete.tmpl"
        MANAGER_REQUEST = _ROOT + "account_manager_request.tmpl"
        MANAGE_REQUEST = _ROOT + "account_manage_request.tmpl"
