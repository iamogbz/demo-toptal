"""
Test jogger app module
"""
import os
from django.test import TestCase


class SettingsTest(TestCase):
    """
    Test app settings
    """

    def test_environment(self):
        """
        Test dot env loaded enviroment settings
        """
        self.assertIsNotNone(os.getenv('SECRET'))
        self.assertIsNotNone(os.getenv('DEBUG'))
        self.assertIsNotNone(os.getenv('DB_NAME'))
        self.assertIsNotNone(os.getenv('DB_TEST'))
