# -*- coding: utf-8 -*-

import cherrypy

from lib.model.user import User, UserModelException, InvalidUser, InvalidCredentials
from lib.model.sshkey import SSHKey, InvalidKey

class AuthTool(object):


  @cherrypy.expose
  @cherrypy.tools.render(template='index.html')
  def index(self, username=None):
    if cherrypy.session.get('auth', False):
      raise cherrypy.HTTPRedirect('/update')
    else:
      return {'username': username}

  @cherrypy.expose
  @cherrypy.tools.render(template='update.html')
  def update(self):
    if not cherrypy.session.get('auth', False):
      raise cherrypy.HTTPRedirect('/')
    else:
      return vars(cherrypy.session['user'])

  @cherrypy.expose
  @cherrypy.tools.render(template='reset.html')
  def reset(self, token=None, username=None):
    if cherrypy.engine.publish('token-verify', token, username).pop():
      cherrypy.session['token'] = token
      cherrypy.session['username'] = username
      return {'ok': True}
    else:
      return {'ok': False}

  @cherrypy.expose
  def logout(self):
    cherrypy.lib.sessions.expire()
    raise cherrypy.HTTPRedirect('/')

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.allowed(allowed_methods=['POST'])
  def login(self, username=None, password=None):
    if username is None or password is None:
      raise cherrypy.HTTPError(400, 'Bad Request')

    try:
      cherrypy.session['user'] = User(username)
      cherrypy.session['auth'] = cherrypy.session['user'].authenticate(password)
      return {'ok': cherrypy.session['user'].auth}
    except (InvalidUser, InvalidCredentials):
      return {
          'ok': False,
          'error': 'Invalid credentials.  Try again.'
          }
    except UserModelException:
      return {'ok': False}

  @cherrypy.expose
  @cherrypy.tools.email()
  @cherrypy.tools.json_out()
  @cherrypy.tools.allowed(allowed_methods=['POST'])
  def forgot(self, emailaddr, email_type):
    if '@' in emailaddr:
      localpart, domain = emailaddr.split('@')
    else:
      localpart = emailaddr
      domain = cherrypy.request.app.config.get('email', {}).get('domain', 'localhost')

    cherrypy.request.email_address = '@'.join([localpart, domain])

    if email_type not in ['password', 'username']:
      raise cherrypy.HTTPError(400)

    cherrypy.request.email_type = email_type

    return {'ok': True}

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.allowed(allowed_methods=['POST'])
  def change(self, **params):
    engine = cherrypy.engine
    if cherrypy.session.get('auth', False):
      user = cherrypy.session['user']
      oldpasswd = cherrypy.request.params.get('oldpassword')
      newpasswd = cherrypy.request.params.get('newpassword')

      try:
        user.change_password(oldpasswd, newpasswd)

        return {'ok': True}
      except InvalidCredentials:
        return {
            'ok': False,
            'error': 'Current password invalid.'
            }
      except UserModelException:
        return {
            'ok': False,
            'error': 'Unknown system error.  Contact your Systems Administrator.'
            }

    elif cherrypy.session.get('token', False):
      cherrypy.session['user'] = User(cherrypy.session['username'])
      newpassword = cherrypy.request.params.get('newpassword')

      try:
        cherrypy.session['user'].set_password(newpassword)
        return {'ok': True}
      except UserModelException:
        return {
            'ok': False,
            'error': 'Unable to change your password. Try again later.'
            }

  @cherrypy.expose
  @cherrypy.tools.json_out()
  @cherrypy.tools.allowed(allowed_methods=['GET', 'POST', 'DELETE'])
  def sshkey(self, sshpubkey=None):
    http_method = cherrypy.request.method.upper()

    if cherrypy.session.get('auth', False):
      user = cherrypy.session['user']
      if http_method == 'POST':
        try:
          newkey = SSHKey(sshpubkey)
          user.add_key(newkey.key)
          return {
              'ok': True,
              'fingerprint': newkey.fingerprint,
              'comment': newkey.comment
              }
        except UserModelException:
            return {'ok': False}
        except InvalidKey:
          return {
              'ok': False,
              'error': 'Not a valid SSH Public Key!'
              }
        else:
          return {'ok': False}

      if http_method == 'DELETE':
        try:
          user.delete_key(sshpubkey)
          return {'ok': True}
        except UserModelException:
          return {'ok': False}

      if http_method == 'GET':
        return user.sshPublicKey
    else:
      raise cherrypy.HTTPError(403)

