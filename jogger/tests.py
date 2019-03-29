"""
Test jogger app module
"""
from django.test import TestCase

from jogger.settings import (
    DB_NAME,
    DB_TEST,
    DEBUG,
    SECRET_KEY,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
)


class SettingsTest(TestCase):
    """
    Test app settings
    """

    def assert_string(self, value, min_length):
        """
        Custom assert string is not None or less than minimum length
        :param value: string to test
        :param min_length: minimum acceptable length
        """
        self.assertIsNotNone(value)
        self.assertGreaterEqual(len(value), min_length)

    def test_environment(self):
        """
        Test dot env loaded enviroment settings
        """
        self.assert_string(SECRET_KEY, 32)
        self.assertIsNotNone(DEBUG)

        self.assert_string(DB_NAME, 1)
        self.assert_string(DB_TEST, 1)
        self.assert_string(SMTP_HOST, 1)
        self.assertIsNotNone(SMTP_PORT)
        self.assert_string(SMTP_USER, 1)
