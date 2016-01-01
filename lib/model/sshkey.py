# -*- coding: utf-8 -*-

import base64
import hashlib
import struct

__all__ = ['SSHKey']

class SSHKey(object):
    """
    An RFC4253 formatted public key with the following attributes:
    """


    def __init__(self, key):
        """
        Parse a valid ssh key and set instance variables for the
        key type, comment, and fingerprint of the key.  Also set an
        instance variable for the key itself.
        """
        self.key = key
        self.key_type, self.key_string, self.key_comment = key.strip().split()
        self._validate_key()
        self.comment = self.key_comment.encode('ascii')
        self.fingerprint = self._fingerprint()

    def _fingerprint(self):
        """
        Return fingerprint of specified public key string.
        """
        b64d_key = base64.b64decode(self.key_string.encode('ascii'))
        fp_plain = hashlib.md5(b64d_key).hexdigest()
        fingerprint = ":".join(a+b for a, b in zip(fp_plain[::2], fp_plain[1::2]))
        return fingerprint

    def _validate_key(self):
        """
        Validates a RFC4253 ssh public key of type ssh-rsa or ssh-dss.

        Checks that the data portion of the key can be base64 decoded and the
        header (first 4 bytes) is '7'.
        """
        try:
            data = base64.decodestring(self.key_string)
            str_len = struct.unpack('>I', data[:4])[0]
            data[4:4 + str_len] == self.key_type # pylint: disable=W0104
        except:
            raise InvalidKey

class SSHKeyException(Exception):
    """
    Base exception class
    """
    pass

class InvalidKey(SSHKeyException):
    """
    SSH Invalid Key exception
    """
    pass
