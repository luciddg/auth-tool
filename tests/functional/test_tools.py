# -*- coding: utf-8 -*-
import cherrypy
from jinja2 import Template
import mock

from tests.utils import BaseToolsTest
from lib.tool.allowed_methods import AllowedMethodsTool
from lib.tool.cpemail import EmailTool
from lib.tool.template import Jinja2Tool

class TestAllowedMethods(BaseToolsTest):

  _cp_config = {
      'tools.allowed.on': True,
      'tools.allowed.allowed_methods': ['GET']
      }

  def setUp(self):
    super(TestAllowedMethods, self).setUp()
    cherrypy.tools.allowed = AllowedMethodsTool()

  def test_allowed(self):
    request, response = self.request('/')
    self.assertEqual(response.output_status, '200 OK')

  def test_disallowed(self):
    request, response = self.request('/', method='POST')
    self.assertEqual(response.output_status, '405 Method Not Allowed')

class TestJinja2Tool(BaseToolsTest):

  _cp_config = {
      'tools.render.on': True,
      'tools.render.template': 'test.html'
      }

  def setUp(self):
    super(TestJinja2Tool, self).setUp()
    cherrypy.tools.render = Jinja2Tool()

