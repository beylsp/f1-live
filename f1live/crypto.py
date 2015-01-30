"""
Crypto operations.
"""
import logging
import http
import struct

__all__ = ['Crypto']

_LOGGER = logging.getLogger(__name__)

CRYPTO_SEED = 0x55555555

class Crypto(object):
    """Basic crypto operations."""

    salt = CRYPTO_SEED

    @classmethod
    def set_user_token(cls, user_token):
        """
        Save the user token needed to download the master key.

        @param user_token: user token from successful login.
        @type user_token: C{string}.
        """
        cls.user_token = user_token

    @classmethod
    def load_decryption_key(cls, event_id):
        """
        Load master decryption key.

        @param event_id: current event id.
        @type event_id: C{int}.
        """
        response = http.get('http://{0}/reg/getkey/{1}.asp'
                          .format(http.F1_LIVE_SERVER, event_id.zfill(5)),
                        params={'auth': cls.user_token})
        cls.key = int(response.get_content(), 16)

    @classmethod
    def reset_decryption_key(cls):
        """
        Reset salt to initial seed.
        """
        cls.salt = CRYPTO_SEED

    @classmethod
    def decrypt(cls, data):
        """
        Decrypt the given data.

        @param data: data the decrypt.
        @type data: C{string}.
        @return: decrypted data.
        @rtype: C{string}.
        """
        dec = []
        for byte in data:
            byte = struct.unpack('B', byte)[0]
            cls.salt = (cls.salt >> 1) ^ (cls.key if cls.salt & 0x01 else 0)
            dec.append(struct.pack('B', byte ^ (cls.salt & 0xff)))
        return ''.join(dec)

