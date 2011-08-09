# -*- coding: utf-8 -*-

import cherrypy

__all__ = ['Jinja2Tool']

class Jinja2Tool(cherrypy.Tool):
  """A Tool that provides Jinja2 functionality."""

  def __init__(self):
    cherrypy.Tool.__init__(self, 'before_finalize',
                           self._render,
                           priority=10)

  def _render(self, template=None):
    """
    Applied once your page handler has been called. It
    looks up the template from the various template directories
    defined in the Jinja2 plugin then renders it with
    whatever dictionary the page handler returned.
    """
    if cherrypy.response.status > 399:
      return

    # retrieve the data returned by the handler
    data = cherrypy.response.body or {}
    template = cherrypy.engine.publish("lookup-template", template).pop()

    if template and isinstance(data, dict):
      cherrypy.response.body = template.render(**data)

