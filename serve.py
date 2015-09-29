# -*- coding: utf-8 -*-

import cherrypy
from cherrypy import _cplogging
import logging
from logging import handlers
from optparse import OptionParser
import os
import sys

class Server(object):
  

  def __init__(self, options):
    self.base_dir = os.path.normpath(os.path.abspath(options.basedir))
    self.conf_path = os.path.join(self.base_dir, "conf")
    
    # git doesn't track empty dirs, so we may need to
    # create the logs dir
    log_dir = os.path.join(self.base_dir, "logs")
    if not os.path.exists(log_dir):
      os.mkdir(log_dir)

    cherrypy.config.update(os.path.join(self.conf_path, "server.cfg"))
    engine = cherrypy.engine

    # amend the system path so Python can find our app modules
    sys.path.insert(0, self.base_dir)

    # template engine tool
    from lib.tool.template import Jinja2Tool
    cherrypy.tools.render = Jinja2Tool()

    # email sending tool
    from lib.tool.cpemail import EmailTool
    cherrypy.tools.email = EmailTool()

    # allowed methods tool
    from lib.tool.allowed_methods import AllowedMethodsTool
    cherrypy.tools.allowed = AllowedMethodsTool()

    # our application
    from webapp import AuthTool
    webapp = AuthTool()
    app = cherrypy.tree.mount(webapp, "/", os.path.join(self.conf_path, "app.cfg"))
    self.make_rotate_logs(app)
    branding = app.config.get("branding", {'appname': 'AuthTool'})

    # template engine plugin
    from jinja2 import Environment, FileSystemLoader
    from lib.plugin.template import Jinja2TemplatePlugin
    env = Environment(loader=FileSystemLoader(os.path.join(self.base_dir, "template")))
    env.globals.update(branding)
    engine.jinja2 = Jinja2TemplatePlugin(cherrypy.engine, env=env)
    engine.jinja2.subscribe()

    # ldap connection plugin
    from lib.plugin.cpldap import LDAPEnginePlugin
    ldap_config = app.config.get("ldap", {})
    engine.ldap = LDAPEnginePlugin(
        engine,
        ldap_config.get("uri", "ldap://localhost:389/"),
        ldap_config.get("base_dn", "ou=people,dc=example,dc=com"),
        ldap_config.get("bind_dn", "cn=admin"),
        ldap_config.get("bind_pw", "admin"),
        ldap_config.get("tls", False),
        ldap_config.get("no_verify", False)
      )
    engine.ldap.subscribe()

    # email sending plugin
    from lib.plugin.cpemail import EmailEnginePlugin
    smtp_config = app.config.get("smtp", {})
    engine.email = EmailEnginePlugin(
        engine,
        smtp_config.get("server", "localhost"),
        smtp_config.get("port", "25"),
        smtp_config.get("user", None),
        smtp_config.get("password", None),
        smtp_config.get("from", "noreply@example.com"),
        subject=branding.get("appname")
      )
    engine.email.subscribe()

    # token generation and lookup plugin
    from lib.plugin.token import TokenEnginePlugin
    token_config = app.config.get("token", {})
    engine.token = TokenEnginePlugin(
        engine,
        token_config.get("secret", "changeme")
      )
    engine.token.subscribe()

    # password hashing plugin
    from lib.plugin.passwd import PasswordEnginePlugin
    engine.passwd = PasswordEnginePlugin(engine)
    engine.passwd.subscribe()

  def run(self):
    engine = cherrypy.engine

    if hasattr(engine, "signal_handler"):
      engine.signal_handler.subscribe()

    if hasattr(engine, "console_control_handler"):
      engine.console_control_handler.subscribe()

    engine.start()
    engine.block()

  def make_rotate_logs(self, app):
    # see http://www.cherrypy.org/wiki/Logging#CustomHandlers
    log = app.log
    
    # Remove the default FileHandlers if present.
    log.error_file = ""
    log.access_file = ""
    
    maxBytes = getattr(log, "rot_maxBytes", 10485760)
    backupCount = getattr(log, "rot_backupCount", 5)
    
    # Make a new RotatingFileHandler for the error log.
    fname = getattr(log, "rot_error_file", "error.log")
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(logging.DEBUG)
    h.setFormatter(_cplogging.logfmt)
    log.error_log.addHandler(h)
    
    # Make a new RotatingFileHandler for the access log.
    fname = getattr(log, "rot_access_file", "access.log")
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(logging.DEBUG)
    h.setFormatter(_cplogging.logfmt)
    log.access_log.addHandler(h)

if __name__ == '__main__':
  def parse_commandline():
    curdir = os.path.normpath(os.path.abspath(os.path.curdir))
    
    parser = OptionParser()
    parser.add_option("-b", "--base-dir", dest="basedir",
                      help="Base directory in which the server "\
                      "is launched (default: %s)" % curdir)
    parser.set_defaults(basedir=curdir)
    (options, args) = parser.parse_args()

    return options

  Server(parse_commandline()).run()

