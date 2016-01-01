# -*- coding: utf-8 -*-

import base64
import hashlib
import os
import smbpasswd

from cherrypy.process import wspbus, plugins

__all__ = ['PasswordEnginePlugin']

class PasswordEnginePlugin(plugins.SimplePlugin):
    """
    The PasswordEnginePlugin is used to generate hashes for supported
    algorithms in the LDAP server.
    """


    def __init__(self, bus):
        """
        This plugin is used to hash a password in suitable digests
        for storage in LDAP.
        """
        plugins.SimplePlugin.__init__(self, bus)

    def start(self): # pragma: no cover
        self.bus.log('Starting up passwd plugin')
        self.bus.subscribe('password-hash', self._hash_password)

    def stop(self): # pragma: no cover
        self.bus.log('Stopping passwd plugin')
        self.bus.unsubscribe('password-hash', self._hash_password)

    def _hash_password(self, password):
        """
        Returns a dict of key value pairs where keys are ldap password
        attributes and values are the hashed passwords
        """
        ssha_hash = self._ssha(password)
        nt_hash = smbpasswd.nthash(password)
        return {
            'sambaNTPassword': nt_hash,
            'userPassword': ssha_hash
        }

    @classmethod
    def _ssha(cls, data):
        """
        Generates a seeded SHA1 password hash.
        """
        salt = os.urandom(4)
        sha1_hash = hashlib.sha1(data)
        sha1_hash.update(salt)
        passwd = '{{SSHA}}{0}'.format(base64.encodestring(sha1_hash.digest() + salt)[:-1])
        return passwd

