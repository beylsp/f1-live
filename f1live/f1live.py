"""
F1 live timing client.
"""
import logging
import sys
import httplib
import config
import http
import streaming
from crypto import Crypto
from twisted.internet import reactor

_LOGGER = logging.getLogger(__name__)

class LoginError(Exception):
    """login error exception."""
    pass

def login(credentials):
    """log on to the f1 live timing web service."""
    email, password = credentials
    response = http.post(url='http://{0}/reg/login'.format(http.F1_LIVE_SERVER),
                  data={'email': email, 'password': password},
                  headers={'User-Agent': __name__,
                           'Content-Type': 'application/x-www-form-urlencoded'})
    if response.get_status_code() != httplib.FOUND: # 302
        raise LoginError("Login failed!")
    return response.get_cookie('USER')

def main():
    """start eventloop."""
    try:
        user_token = login(config.get_credentials())
        if not user_token:
            raise LoginError("Invalid user token cookie!")
        Crypto.set_user_token(user_token)
        reactor.connectTCP(http.F1_LIVE_SERVER, 4321,
                           streaming.StreamingClientFactory())
    except LoginError as err:
        print str(err) + " Please try again."
        config.remove_credentials()
        sys.exit(1)
    except http.ConnectionError as err:
        print str(err)
        sys.exit(1)
    else:
        reactor.run()

if __name__ == '__main__':
    main()
