"""
Simple HTTP requests library.
"""
import socket
from httplib2 import Http
from httplib2 import ServerNotFoundError
from urllib import urlencode
from Cookie import BaseCookie

__all__ = ['get', 'post']

class ConnectionError(Exception):
    """connection error exception."""
    pass

def request(method, url,
    	params=None,
	data=None,
        headers=None):
    """do an http request."""
    try:
        if params:
            url = "{0}?{1}".format(url, urlencode(params))
        response, _ = Http().request(url, method.upper(),
                                     urlencode(data), headers)
    except (ServerNotFoundError, socket.error) as err:
        raise ConnectionError(str(err))
    return Response(response)

def get(url, **kwargs):
    """
    Do an http GET request.

    @param url: http request url.
    @type url: C{string}.
    @param **kwargs: url request parameters as key-value pairs.
    @type **kwargs: dict.
    @return: http response.
    @rtype C{Response}.
    """
    return request('get', url, **kwargs)

def post(url, data=None, **kwargs):
    """
    Do a http POST request.

    @param url: http request url.
    @type url: C{string}.
    @param **kwargs: url request parameters as key-value pairs.
    @type **kwargs: dict.
    @return: http response.
    @rtype C{Response}.
    """
    return request('post', url, data=data, **kwargs)

class Response(object):
    """http response object."""
    def __init__(self, response):
        self.status_code = int(response['status'])
        self.cookies = dict()
        try:
            set_cookie = response['set-cookie']
        except KeyError:
            pass
        else:
            for key, val in BaseCookie(set_cookie).items():
                self.cookies[key] = val.value

    def get_status_code(self):
        """
        Returns the http status code.

        @return: http response status code.
        @rtype: C{int}.
        """
        return self.status_code

    def get_cookie(self, cookie):
        """
        Returns the value for cookie.

        @param cookie: cookie to retrieve.
        @type cookie: C{string}.
        @return: value of cookie.
        @rtype: C{string}.
        """
        try:
            return self.cookies[cookie.upper()]
        except KeyError:
            return None

