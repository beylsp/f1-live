"""
A lightweight implementation of a Firebase REST endpoint
mimicking the javascript APIs.
"""
import logging
import http
import json
import urlparse
import os

__all__ = ['Firebase']

log = logging.getLogger(__name__)

class Firebase(object):
    """Firebase reference object."""
    def __init__(self, url):
        self.root_url = url.rstrip('/')

    def child(self, path):
        """
        Get a Firebase reference for the location at the specified
        relative path.

        @param path: relative path from this location to the desired
                     child location.
        @type path: C{string}.
        @return: Firebase reference to the specified child location.
        @rtype: C{Firebase}.
        """
        root_url = '{0}/'.format(self.root_url)
        url = urlparse.urljoin(root_url, path.rstrip('/'))
        return Firebase(url)

    def parent(self):
        """
        Get a Firebase reference to the parent location.

        @return: Firebase reference to the parent location, or None if this
                 instance refers to the root of your Firebase.
        @rtype: C{Firebase}.
        """
        url = os.path.dirname(self.root_url)
        up = urlparse.urlparse(url)
        if up.path == '':
            return None
        return Firebase(url)

    def root(self):
        """
        Get a Firebase reference to the root of the Firebase.

        @return: Firebase reference to the root of your Firebase.
        @rtype: C{Firebase}.
        """
        url = os.path.dirname(self.root_url)
        up = urlparse.urlparse(url)
        return Firebase(up.netloc)

    def key(self):
        """
        Return the last token in a Firebase location.

        @return: last token of this location.
        @rtype: C{string}.
        """
        return os.path.basename(self.root_url)

    def toString(self):
        """
        Get the absolute URL corresponding to this Firebase reference's
        location.

        @return: absolute URL corresponding to this location.
        @rtype: C{string}.
        """
        return self.__str__()

    def __str__(self):
        return self.root_url

    def set(self, data):
        """
        Write or replace data to a defined path, like
        'messages/users/<username>'.

        @param data: data to be written.
        @type data: C{dict}.
        """
        self.request('put', data=data)

    def update(self, data):
        """
        Update some of the keys for a defined path without
        replacing all of the data.

        @param data: dict containing children and their values to be written.
        @type data: C{dict}.
        """
        self.request('patch', data=data)

    def remove(self):
        """
        Remove the data at this Firebase location.
        """
        self.request('delete')

    def push(self, data):
        """
        Add to a list of data in Firebase. Every time push() is invoked,
        Firebase generates a unique ID, like
        'messages/users/<unique-user-id>/<username>'.

        @param data: value to be written at the generated location.
        @type data: C{dict}
        @return: Firebase reference for the generated location.
        @rtype: C{Firebase}.
        """
        ref = self.request('post', data=data)
        url = urlparse.urljoin(self.root_url, ref['name'])
        return Firebase(url)

    def request(self, method, **kwargs):
        """do an http request."""
        response = http.request(method, self.url(),
                                encode=json.dumps, **kwargs)
        if response.ok:
            return json.loads(response.get_content())

    def url(self):
        """append json extension to root url."""
        return '{0}.json'.format(self.root_url)

