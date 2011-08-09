#!/usr/bin/env/python

import os, sys
import cherrypy
from cherrypy import tools
from lib import template
import ldap
import smbpasswd
#smbpasswd.nthash!
from lib import sha
from lib import mkpass
from lib import smail

class Root(object):

  @cherrypy.expose
  @template.output('index.html')
  def index(self, **data):
    if dict(**data):
      if dict(**data)['error'] == 'True':
        return template.render(error=1)
    else:
      return template.render(error=0)

  @cherrypy.expose
  @template.output('password.html')
  def login(self, **data):
    data = dict(**data)
    try: 
      con = ldap.initialize('ldap://localhost')
      dn = 'uid=' + data['username'] + ',ou=people,dc=luciddg,dc=com'
      con.simple_bind_s(dn,data['password'])
      con.unbind_s()
      return template.render(username=data['username'])
    except:
      print 'failed to bind '  
      raise cherrypy.InternalRedirect('/?error=True')

  @cherrypy.expose
  @template.output('results.html')
  def lost(self, **data):
    results = []
    data = dict(**data)
    user_dn = 'uid=' + data['lost_username'] + ',ou=people,dc=luciddg,dc=com'
    newpass = mkpass.GenPasswd2(13)
    ssha = sha.makeSecret(newpass)
    nt = smbpasswd.nthash(newpass)
    try:
      con = ldap.initialize('ldap://localhost')
      dn = 'cn=admin,dc=luciddg,dc=com'
      pw = 'secret'
      con.simple_bind_s(dn,pw)
    except:
      results.append('Error connecting to ldap')
      return template.render(results=results)
    try: 
      con.compare_s(user_dn,'uid',data['lost_username'])
    except:
      results.append('Invalid user')
      return template.render(results=results)
    try:
      mail = con.search_s(user_dn,ldap.SCOPE_SUBTREE,'(objectclass=ldgOrgPerson)',['mail'])[0][1]['mail'][0]
    except:
      results.append('You do not have an email address on file')
      return template.render(results=results)
    try:
      mod_ssha = [(ldap.MOD_REPLACE, 'userPassword', ssha)]
      con.modify_s(user_dn,mod_ssha)
      results.append('Updated user password (wiki, etc.)')
    except:
      results.append('Error updating user password (wiki, etc.)')
    try:
      mod_ntpw = [(ldap.MOD_REPLACE, 'sambaNTPassword', nt)]
      con.modify_s(user_dn,mod_ntpw)
      results.append('Updated fileserver password')
    except:
      results.append('Error updating fileserver password')
    try:
      con.unbind_s()
    except:
      pass
    try:
      smail.sendMsg(mail,newpass)
      results.append('Your new password has been emailed to ' + mail + '. Please return here to reset it.')
    except:
      results.append('Error sending mail to ' + mail)
    return template.render(results=results)
    
  @cherrypy.expose
  @template.output('results.html')
  def change_pass(self, **data):
    data = dict(**data)
    results = []
    if data:
      if data['newpass1'] == data['newpass2'] and len(data['newpass1']) > 7:
        ssha = sha.makeSecret(data['newpass1'])
        nt = smbpasswd.nthash(data['newpass1'])
        try:
          dn = 'uid=' + data['username'] + ',ou=people,dc=luciddg,dc=com'
          con = ldap.initialize('ldap://localhost')
          con.simple_bind_s(dn,data['password'])
        except:
          results.append('Current password entered is invalid.')
          return template.render(results=results)
        try:
          mod_ssha = [(ldap.MOD_REPLACE, 'userPassword', ssha)]
          con.modify_s(dn,mod_ssha)
          results.append('Updated user password (wiki, etc.)')
        except:
          results.append('Error updating user password (wiki, etc.)')
        try:
          mod_ntpw = [(ldap.MOD_REPLACE, 'sambaNTPassword', nt)]
          con.modify_s(dn,mod_ntpw)
          results.append('Updated fileserver password')
        except:
          results.append('Error updating fileserver password')
        try:
          con.unbind_s()
        except:
          pass
        return template.render(results=results)
      else:
        results.append('Passwords do not match or password too short (8 chars min)')
        return template.render(results=results)
    else:
      results.append('ERROR! Contact sysadmin')
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
