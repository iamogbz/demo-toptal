"""
Test jogger app module
"""
import os
from django.test import TestCase


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
        self.assert_string(os.getenv('SECRET'), 32)
        debug_flag = int(os.getenv('DEBUG'))
        self.assertIsNotNone(debug_flag)

        self.assert_string(os.getenv('DB_NAME'), 1)
        self.assert_string(os.getenv('DB_TEST'), 1)
        self.assert_string(os.getenv('SMTP_HOST'), 1)

        smtp_port = int(os.getenv('SMTP_PORT'))
        self.assertIsNotNone(smtp_port)
        self.assert_string(os.getenv('SMTP_USER'), 1)
