"""
Simple HTTP requests library.
"""
import socket
from httplib2 import Http
from httplib2 import ServerNotFoundError
from urllib import urlencode
from Cookie import BaseCookie
from StringIO import StringIO
from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.client import FileBodyProducer
from twisted.internet.protocol import Protocol

__all__ = ['get', 'get_async', 'post', 'post_async']

F1_LIVE_SERVER = 'live-timing.formula1.com'

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
        if data:
            data = urlencode(data)
        response, _ = Http().request(url, method.upper(),
                                     data, headers)
    except (ServerNotFoundError, socket.error) as err:
        raise ConnectionError(str(err))
    return Response(response)

def request_async(defer, method, url,
             params=None,
             data=None,
             headers=None):
    """do an asynchronous http request."""
    if params:
        url = "{0}?{1}".format(url, urlencode(params))
    if data:
        data = FileBodyProducer(StringIO(urlencode(data)))
    _defer = Agent(reactor).request(method.upper(), url, headers, data)
    _defer.addCallback(on_http_response, defer)

def on_http_response(response, defer):
    """callback function when http response is received."""
    return response.deliverBody(HttpBodyConsumer(response.length, defer))

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

def get_async(defer, url, **kwargs):
    """
    Do an asynchronous http GET request.

    @param defer: deferred object with callback functions to be called
                  when http response is received.
    @type defer: C{Deferred}.
    @param url: http request url.
    @type url: C{string}.
    @param **kwargs: url request parameters as key-value pairs.
    @type **kwargs: dict.
    """
    return request_async(defer, 'get', url, **kwargs)

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

def post_async(defer, url, data=None, **kwargs):
    """
    Do an asynchronous http POST request.

    @param defer: deferred object with callback functions to be called
                  when http response is received.
    @type defer: C{Deferred}.
    @param url: http request url.
    @type url: C{string}.
    @param **kwargs: url request parameters as key-value pairs.
    @type **kwargs: dict.
    """
    return request_async(defer, 'post', url, data=data, **kwargs)

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


class HttpBodyConsumer(Protocol):
    """asynchronous http response consumer."""
    def __init__(self, length, finished):
        self.remaining = length
        self.finished = finished
        self.body = ''

    def dataReceived(self, data):
        if self.remaining:
            self.body += data[:self.remaining]
            self.remaining -= len(data)

    def connectionLost(self, reason):
        self.finished.callback(self.body)

