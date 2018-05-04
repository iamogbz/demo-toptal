"""
Test utility module
"""
from django.test import SimpleTestCase
from rest_framework.exceptions import APIException

from api.utils import (
    has_required,
    raise_api_exc,
)


class UtilsTest(SimpleTestCase):
    """
    Test helper functions
    """

    def test_has_required(self):
        """
        Test utils.has_required function
        """
        self.assertTrue(has_required({1, 2, 3, 4}, {2, 3}))
        self.assertFalse(has_required({1, 2, 3, 4}, {2, 3, 99}))

    def test_raise_api_exec(self):
        """
        Test utils.raise_api_exec function
        """
        status_code = 419
        with self.assertRaises(APIException):
            try:
                raise_api_exc(APIException(), status_code)
            except APIException as exc:
                self.assertEqual(exc.status_code, status_code)
                raise exc
