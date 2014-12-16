#!/usr/bin/env/python

import os, sys, site

appDir = os.path.dirname(os.path.realpath( __file__ ))
vEnv = '/opt/luciddg-ds-passmgr/.virtualenv/v/lib/python2.6/site-packages'

prev_sys_path = list(sys.path)

site.addsitedir(vEnv)
site.addsitedir(appDir)

new_sys_path = [] 

for item in list(sys.path): 
  if item not in prev_sys_path: 
    new_sys_path.append(item) 
    sys.path.remove(item) 

sys.path[:0] = new_sys_path 

import cherrypy
from classes import PassMgr

cherrypy.config.update({'environment': 'embedded'})
sys.stdout = sys.stderr

if cherrypy.__version__.startswith('3.2') and cherrypy.engine.state == 0:
  cherrypy.engine.start(blocking=False)
  atexit.register(cherrypy.engine.stop)
  
application = cherrypy.Application(PassMgr.PassMgr(), script_name=None, config=None)

