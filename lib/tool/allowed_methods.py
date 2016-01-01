# -*- coding: utf-8 -*-

import cherrypy

__all__ = ['AllowedMethodsTool']

class AllowedMethodsTool(cherrypy.Tool):
    """
    The AllowedMethods tool is responsible for checking each
    request for a method matching the allowed methods.

    If the method is not allowed, a 405 (Method Not Allowed) is
    raised.
    """

    # HTTP Methods as listed in RFC2616 and RFC5789
    VALID_METHODS = ['GET',
                     'HEAD',
                     'POST',
                     'PUT',
                     'DELETE',
                     'TRACE',
                     'OPTIONS',
                     'CONNECT',
                     'PATCH',
                    ]

    def __init__(self):
        cherrypy.Tool.__init__(self, "on_start_resource",
                               self._check_method,
                               priority=10)

    @classmethod
    def _check_method(cls, allowed_methods=VALID_METHODS):
        """
        Validate the request method is in the set of allowed methods.
        If not, set the Allow header to the list of allowed methods and
        return a 405 (Method Not Allowed).
        """
        if cherrypy.request.method.upper() not in allowed_methods:
            cherrypy.response.headers['Allow'] = (', ').join(allowed_methods)
            raise cherrypy.HTTPError(405)
