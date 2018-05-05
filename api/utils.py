"""
Utility functions for api module
"""
import re
import smtplib
from email.mime.text import MIMEText

from api.constants import (
    MAIL_HOST,
    MAIL_PORT,
)


def peek(bucket):
    """
    Get first element of set without removing
    :param bucket: set to peek
    """
    elem = None
    for elem in bucket:
        break
    return elem


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


def replace(string, replxs):
    """
    Given a string and a replacement map, it returns the replaced string.
    https://goo.gl/7fcBpE
    :param str string: string to execute replacements on
    :param dict replxs: replacement map {value to find: value to replace}
    :rtype: str
    """
    substrs = sorted(replxs, key=len, reverse=True)
    regexp = re.compile('|'.join(map(re.escape, substrs)))
    return regexp.sub(lambda match: replxs.get(match.group(0), ''), string)


def send_mail(sender, recievers, subject, tmpl_file, tmpl_data):
    """
    Send mail using localhost smtp
    :param str sender: email to send from
    :param list recievers: list of emails to send to
    :param str subject: the email subject
    :param str tmpl_file: file path to use as email body template
    :param dict tmpl_data: keys to string replacement for email template
    """
    msg = ''
    with open(tmpl_file, 'r') as fstream:
        msg = MIMEText(fstream.read())
    msg.preamble = subject
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recievers)
    msg = replace(msg.as_string(), tmpl_data)

    smtp = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    smtp.sendmail(sender, recievers, msg)
    smtp.quit()
    return msg
