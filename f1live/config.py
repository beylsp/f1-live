"""
Config file parsing and creation.
"""
import logging
import sys
import os
from pytools.cli import ask

__all__ = ['get_credentials', 'remove_credentials']

_LOGGER = logging.getLogger(__name__)

CONFIG_FILE = '.f1rc'
EMAIL = 'email'
PASSWORD = 'password'

def get_credentials():
    """
    Retrieve credentials from .f1rc file. First time (or in case of an
    error) the email address and password shall be asked (again) and saved.

    @return: email address and password.
    @rtype: C{tuple}.
    """
    try:
        config = dict(line.strip().split('=', 1) for line in open(CONFIG_FILE))
        return (config[EMAIL], config[PASSWORD])
    except (IOError, ValueError):
        email, password = ask_credentials()
        store_credentials(email, password)
        return (email, password)

def ask_credentials():
    """asks for credentials and returns them."""
    hint()
    email = password = ''
    while not email:
        email = ask('Enter your registered e-mail address: ')
    while not password:
        password = ask('Enter your registered password: ')
    return email, password

def store_credentials(email, password):
    """stores credentials to config file."""
    try:
        with open(CONFIG_FILE, 'w') as _file:
            _file.write('{0}={1}\n'.format(EMAIL, email))
            _file.write('{0}={1}\n'.format(PASSWORD, password))
    except IOError as err:
        print str(err)
        sys.exit(1)

def remove_credentials():
    """"removes credentials file."""
    try:
        os.remove(CONFIG_FILE)
    except IOError as err:
        print str(err)
        sys.exit(1)

def hint():
    """hints why credentials are needed."""
    print
    print "In order to connect to the Live Timing stream, " + \
          "you need to be registered."
    print "if you've not yet done so, " + \
          "do so now by filling out the registration form at the URL:"
    print "http://www.formula1.com/reg/registration"
    print

