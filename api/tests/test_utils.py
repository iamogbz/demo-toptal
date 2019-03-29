"""
Test utility module
"""
from unittest.mock import patch
from email.mime.text import MIMEText
from django.test import SimpleTestCase
from django.utils.crypto import get_random_string
from rest_framework.exceptions import APIException

from api.utils import (
    has_required,
    peek,
    raise_api_exc,
    replace,
    send_mail,
)


class UtilsTest(SimpleTestCase):
    """
    Test helper functions
    """

    def test_peek(self):
        """
        Test peek function
        """
        bucket = set(get_random_string(32))
        self.assertEqual(peek(bucket), bucket.pop())

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

    def test_multireplace(self):
        """
        Test utils.replace function
        """
        str_to_replace = "please replace me with nice things"
        replace_map = {
            'please': 'bloody',
            'replace': 'please',
            'bloody': 'whyyy!!!',
            'things': 'flowers',
        }
        result = replace(str_to_replace, replace_map)
        self.assertEqual(result, 'bloody please me with nice flowers')

    @patch('api.utils.replace', autospec=True)
    def test_send_mail(self, mock_replace):
        """
        Test mail sending function
        """
        sender = 'mailsender@example.com'
        receivers = [
            'longreciever@example.com',
            'shortreceiver@example.com',
        ]
        subject = 'this is a subject'
        message = MIMEText('')
        message.preamble = subject
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = ', '.join(receivers)
        mock_replace.return_value = message.as_string()
        message_data = {'test': 'me'}
        res = send_mail(sender, receivers, subject, '/dev/null', message_data)
        mock_replace.assert_called_with(message.as_string(), message_data)
        self.assertIsNotNone(res)
