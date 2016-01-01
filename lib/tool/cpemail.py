# -*- coding: utf-8 -*-

import cherrypy

from lib.model.user import User

__all__ = ['EmailTool']

class EmailTool(cherrypy.Tool):
    def __init__(self):
        """
        The Email Tool provides functionality for sending password
        reset emails in the background rather than blocking
        the request.    The user should not be made aware of success
        or failure, so all error handling is logged.
        """
        cherrypy.Tool.__init__(self, 'on_end_request',
                               self._send_email,
                               priority=80)


    @classmethod
    def _send_email(cls):
        """
        Check the email type and send the requested email using
        the email plugin.
        """
        if not hasattr(cherrypy.request, 'email_address'):
            return

        if not hasattr(cherrypy.request, 'email_type'):
            return

        cherrypy.request.user = User.get_by_email(cherrypy.request.email_address)

        if 'mail' in cherrypy.request.user:
            if cherrypy.request.email_type == 'password':
                cherrypy.engine.publish('email-send-reset', cherrypy.request.user)
            if cherrypy.request.email_type == 'username':
                cherrypy.engine.publish('email-send-username', cherrypy.request.user)
