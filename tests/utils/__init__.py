import cherrypy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.utils.cptestcase import BaseCherryPyTestCase
from serve import Server


class Root(object):
    """
    The simplest CherryPy app needed to test individual tools
    """

    _cp_config = {}

    @cherrypy.expose
    def index(self):
        return {'return': ['Hello world.']}

    @cherrypy.expose
    def echo(self, msg):
        return msg


class BaseToolsTest(BaseCherryPyTestCase):
    """
    A base class so tests can selectively turn individual tools on for testing.
    """

    def setUp(self):
        Root._cp_config = self._cp_config
        root = Root()
 
        cherrypy.tree.mount(root, '/')
        cherrypy.server.unsubscribe()
        cherrypy.engine.start()

    def tearDown(self):
        cherrypy.engine.exit()

