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
        secret_key = os.getenv('SECRET')
        self.assertIsNotNone(secret_key)
        self.assertGreater(len(secret_key), 32)

        debug_flag = os.getenv('DEBUG')
        self.assertIsNotNone(debug_flag)
        self.assertEqual(len(debug_flag), 1)

        db_name = os.getenv('DB_NAME')
        self.assertIsNotNone(db_name)
        self.assertGreater(len(db_name), 0)

        db_test = os.getenv('DB_TEST')
        self.assertIsNotNone(db_test)
        self.assertGreater(len(db_test), 0)
