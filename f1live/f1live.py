"""
F1 live timing client.
"""
import logging
import sys
import twisted
import httplib
from f1live import config
from f1live import http
from f1live import streaming

_LOGGER = logging.getLogger(__name__)
SERVER = 'live-timing.formula1.com'

class LoginError(Exception):
    """login error exception."""
    pass

def login(credentials):
    """log on to the f1 live timing web service."""
    email, password = credentials
    response = http.post(url='http://{0}/reg/login'.format(SERVER),
                  data={'email': email, 'password': password},
                  headers={'User-Agent': __name__,
                           'Content-Type': 'application/x-www-form-urlencoded'})
    if response.get_status_code() != httplib.FOUND: # 302
        raise LoginError("Login failed!")
    return response.get_cookie('USER')

def main():
    """start eventloop."""
    try:
        user = login(config.get_credentials())
        if not user:
            raise LoginError("Invalid user cookie!")
        twisted.internet.reactor.connectTCP(SERVER, 4321,
                           streaming.StreamingClientFactory(user))
    except LoginError as err:
        print str(err) + " Please try again."
        config.remove_credentials()
        sys.exit(1)
    except http.ConnectionError as err:
        print str(err)
        sys.exit(1)
    else:
        twisted.internet.reactor.run()

if __name__ == '__main__':
    main()
