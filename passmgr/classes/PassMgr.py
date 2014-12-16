import os, sys
import cherrypy
import simplejson
from lib import template
from lib import smail
from lib import ds
from lib import strongpw
from lib import tokenlib

class PassMgr(object):

  @cherrypy.expose
  @template.output('index.html')
  def index(self):
    return template.render(error=0)

  @cherrypy.expose
  def login(self,username,password):
    errors = []
    if not username or not password:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return '"Error: missing username or password"'
    if ds.authenticate(username, password) != 1:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return simplejson.dumps(ds.authenticate(username,password))
    else:
      return username

  @cherrypy.expose
  @template.output('change.html')
  def update(self,username):
    return template.render(username=username,errors=False,token=False)

  @cherrypy.expose
  def lost(self, lost_username):
    results = []
    if not lost_username:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return '"Error: you must enter a username"'
    email = ds.getEmail(lost_username)
    if not email:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return '"Error: No email address available for that username."'
    newToken = tokenlib.generate(lost_username)
    if newToken:
      try:
        smail.sendMsg(email,newToken)
        cherrypy.response.headers['Content-Type'] = 'application/json'        
        return '"An email with a reset link has been sent to your address on file."'
      except:
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return '"Error: there was a glitch sending your password reset email; sorry."'
    else:
      return '"Error: could not generate token, sorry."'

  @cherrypy.expose
  @template.output('change.html')
  def reset(self, token):
    results = []
    errors = []
    tokenUser = tokenlib.verify(token)
    if tokenUser:
      return template.render(username=tokenUser,token=token,errors=False)
    else:
      errors.append('No valid tokens found. Tokens are single-use and valid for only 5 minutes.')
      return template.render(errors=errors,username=False,token=False)
    
  @cherrypy.expose
  def change_pass(self,username,newpass1,newpass2,password='',token=''):
    results = []
    if not password and not token:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return '"Error: current password required"'
    if newpass1 == newpass2:
      if strongpw.check(newpass1,username):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return simplejson.dumps(strongpw.check(newpass1,username))
      else:
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if token and not password:
          results = ds.passwd(username, newpass1, token=token)
        elif password and not token:
          results = ds.passwd(username, newpass1, oldpw=password)
        return simplejson.dumps(results)
    else:
      cherrypy.response.headers['Content-Type'] = 'application/json'
      return '"Error: passwords do not match"'

