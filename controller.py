#!/usr/bin/env/python

import os, sys
import cherrypy
from cherrypy import tools
from lib import template
import ldap
import cPickle as pickle
import datetime
# use smbpasswd.nthash to generate smb pass
import smbpasswd
from lib import smail
from lib import ds
from lib import strongpw
from lib import mkpass

baseURL = 'http://dev4.office.luciddg.com:8080'

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
      with open('.tokens.pck', 'rb') as tokenPck:
        pckData = pickle.load(tokenPck)
    except:
      pckData = []
    pckData.append(tokenData)
    with open('.tokens.pck', 'wb') as tokenPck:
      pickle.dump(pckData,tokenPck)
    try:
      smail.sendMsg(email,url)
      results.append('An email with a reset link has been sent.')
    except:
      results.append('There was an error sending email. Please contact sysadmin.')
    return template.render(results=results)

  @cherrypy.expose
  @template.output('reset.html')
  def reset(self, token):
    results = []
    errors = []
    now = datetime.datetime.utcnow()
    try:
      with open('.tokens.pck','rb') as tokenPck:
        pckData = pickle.load(tokenPck)
        if len(pckData) > 0:
          for dict in pckData:
            if dict['token'] == token:
              tokenData = dict
      pckData[:] = [d for d in pckData if d.get('token') != token]
      with open('.tokens.pck','wb') as pckFile:
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
      return template.render(results=results)

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
      return template.render(results=results)


def main():

    # Some global configuration; note that this could be moved into a
    # configuration file 
    cherrypy.config.update({
        'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
        'tools.decode.on': True,
        'tools.trailing_slash.on': True,
        'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
        'server.socket_host': '0.0.0.0',
    })  

    cherrypy.quickstart(Root(), '/', {
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'media'
        }   
    })  

if __name__ == '__main__':
    main()
