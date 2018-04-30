"""
Api constants
"""


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
