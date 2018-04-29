"""
Utility functions for api module
"""


def has_required(bucket, required):
    """
    Check if all values in required set exist in bucket
    :param bucket: set of values to check
    :param required: set of required values
    :returns bool: True if bucket contains all required
    """
    return required <= bucket


def raise_api_exc(exc, status_code):
    """
    Helper method to raise api exception with status code
    """
    exc.status_code = status_code
    raise exc
