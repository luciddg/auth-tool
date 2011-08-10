#!/usr/bin/env/python

import sys, os
import site

appDir = os.path.dirname(os.path.realpath( __file__ ))
tokenFile = appDir + '/.tokens.pck'

prev_sys_path = list(sys.path) 
vEnv = '/opt/luciddg-ds-passmgr/.virtualenv/v/lib/python2.6/site-packages'
site.addsitedir(vEnv)
site.addsitedir(appDir)

new_sys_path = [] 
for item in list(sys.path): 
  if item not in prev_sys_path: 
    new_sys_path.append(item) 
    sys.path.remove(item) 
sys.path[:0] = new_sys_path 

import cherrypy
from cherrypy import tools
import ldap
import cPickle as pickle
import datetime
import smbpasswd
from lib import template
from lib import smail
from lib import ds
from lib import strongpw
from lib import mkpass
import threading
import atexit
sys.stdout = sys.stderr

baseURL = 'https://password.office.luciddg.com'

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.2') and cherrypy.engine.state == 0:
  cherrypy.engine.start(blocking=False)
  atexit.register(cherrypy.engine.stop)

class Root(object):

  @cherrypy.expose
  @template.output('index.html')
  def index(self, **data):
    if dict(**data):
      if dict(**data)['error']:
        return template.render(error=dict(**data)['error'])
    else:
      return template.render(error=0)

  @cherrypy.expose
  @template.output('change.html')
  def update(self, **data):
    data = dict(**data)
    if not data['username'] or not data['password']:
      raise cherrypy.InternalRedirect('/?error=Missing Field')
    if ds.authenticate(data['username'], data['password']) != 1:
      error = ds.authenticate(data['username'], data['password'])
      error_str = '/?error=' + error.strip()
      raise cherrypy.InternalRedirect(error_str)
    else:
      return template.render(username=data['username'])

  @cherrypy.expose
  @template.output('results.html')
  def lost(self, **data):
    results = []
    data = dict(**data)
    token = mkpass.GenPasswd2(17)
    url = baseURL + '/reset?token=' + token
    now = datetime.datetime.utcnow()
    email = ds.getEmail(data['lost_username'])
    if not email:
      results.append('No email address on file. Contact sysadmin@luciddg.com.')
      return template.render(results=results)
    tokenData = { 'timestamp' : now, 'token' : token, 'uid' : data['lost_username'] }
    try:
      with open(tokenFile, 'rb') as tokenPck:
        pckData = pickle.load(tokenPck)
    except:
      pckData = []
    pckData.append(tokenData)
    with open(tokenFile, 'wb') as tokenPck:
      pickle.dump(pckData,tokenPck)
    try:
      smail.sendMsg(email,url)
      results.append('An email with a reset link has been sent.')
    except:
      results.append('There was an error sending email. Please contact sysadmin.')
    return template.render(results=results,notes=False)

  @cherrypy.expose
  @template.output('reset.html')
  def reset(self, token):
    results = []
    errors = []
    now = datetime.datetime.utcnow()
    try:
      with open(tokenFile,'rb') as tokenPck:
        pckData = pickle.load(tokenPck)
        if len(pckData) > 0:
          for dict in pckData:
            if dict['token'] == token:
              tokenData = dict
      pckData[:] = [d for d in pckData if d.get('token') != token]
      with open(tokenFile,'wb') as pckFile:
          pickle.dump(pckData,pckFile)
      duration = now - tokenData['timestamp']
      if duration.seconds < 360:
        return template.render(username=tokenData['uid'],errors=False)
    except:
      errors.append('No valid tokens found. Tokens are single-use and valid for only 5 minutes.')
      return template.render(errors=errors,username=False)
    
  @cherrypy.expose
  @template.output('results.html')
  def change_pass(self, **data):
    data = dict(**data)
    results = []
    if data:
      if data['newpass1'] == data['newpass2']:
        if strongpw.check(data['newpass1']):
          results += strongpw.check(data['newpass1'])
          return template.render(results=results)
        else:
          results += ds.passwd(data['username'],data['newpass1'],data['password'])
          return template.render(results=results)
      else:
        results.append('Passwords do not match')
        return template.render(results=results)
    else:
      results.append('ERROR! Contact sysadmin (missing form data)')
      return template.render(results=results,notes=True)

  @cherrypy.expose
  @template.output('results.html')
  def reset_pass(self, **data):
    data = dict(**data)
    results = []
    if data:
      if data['newpass1'] == data['newpass2']:
        if strongpw.check(data['newpass1']):
          results += strongpw.check(data['newpass1'])
          return template.render(results=results)
        else:
          results += ds.passwd(data['username'],data['newpass1'])
          return template.render(results=results)
      else:
        results.append('Passwords do not match')
        return template.render(results=results)
    else:
      results.append('ERROR! Contact sysadmin (missing form data)')
      return template.render(results=results,notes=True)

application = cherrypy.Application(Root(), script_name=None, config=None)

