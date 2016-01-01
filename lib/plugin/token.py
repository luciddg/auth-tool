# -*- coding: utf-8 -*-

import hmac
import hashlib
import math
import time

from cherrypy.process import plugins

__all__ = ['TokenEnginePlugin']

class TokenEnginePlugin(plugins.SimplePlugin):
    """
    Generates and verifies RFC-6238-compliant time-based one-time passwords.

    Uses the SHA256 digest algorithm and the TOTP = (K, T) where T is the current
    epoch time divided by the timestep (default 24 hours).  This obviates the need
    to expire or track tokens and pushes the data storage problem onto the client.
    """


    def __init__(self, bus, secret=None, timestep=86400):
        plugins.SimplePlugin.__init__(self, bus)
        self.secret = secret
        self.timestep = timestep

    def start(self): # pragma: no cover
        self.bus.log('Starting token plugin')
        self.bus.subscribe("token-gen", self._gen_token)
        self.bus.subscribe("token-verify", self._verify_token)

    def stop(self): # pragma: no cover
        self.bus.log('Stopping token plugin')
        self.bus.unsubscribe("token-gen", self._gen_token)
        self.bus.unsubscribe("token-verify", self._verify_token)

    def _gen_token(self, data):
        """
        Returns a RFC6238-compliant time-based one-time password
        """
        epoch = math.floor(time.time() / self.timestep)
        return hmac.new(self.secret, str(data) + str(epoch), hashlib.sha256).hexdigest()

    def _verify_token(self, totphash, data):
        """
        Verifies a RFC6238-compliant time-based one-time password.
        Returns True or False.
        """
        epoch = math.floor(time.time() / self.timestep)
        curtimeseries = hmac.new(self.secret,
                                 str(data) + str(epoch),
                                 hashlib.sha256).hexdigest()
        prevtimeseries = hmac.new(self.secret,
                                  str(data) + str(epoch - 1),
                                  hashlib.sha256).hexdigest()

        if totphash == curtimeseries or totphash == prevtimeseries:
            return True
        else:
            return False

