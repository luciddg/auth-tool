import ldap
import smbpasswd

import sha
import tokenlib

ldapURI = 'ldap://10.11.12.10'
baseDN = 'ou=people,dc=luciddg,dc=com'
adminDN = 'uid=passmgr,dc=luciddg,dc=com'
adminPw = '3WT|78XoQ'

def authenticate(uid,password):
  cx = ldap.initialize(ldapURI)
  dn = 'uid=' + uid + ',' + baseDN
  try:
    cx.simple_bind_s(dn,password)
    cx.unbind_s()
    return 1
  except ldap.LDAPError, e:
    error = 'Error: ' + e.message['desc']
    return error

def passwd(uid,newpw,oldpw='',token=''):
  results = []
  ssha = sha.passwd(newpw)
  nt = smbpasswd.nthash(newpw)
  userDN = 'uid=' + uid + ',' + baseDN
  if oldpw and token:
    return ['Error: cannot use both token and old password.']
  if not oldpw and not token:
    return ['Error: old password or reset token required.']
  try:
    cx = ldap.initialize(ldapURI)
    if oldpw:
      cx.simple_bind_s(userDN,oldpw)
    else:
      if tokenlib.verify(token):
        cx.simple_bind_s(adminDN,adminPw)
        tokenlib.delete(token)
      else:
        return ['Error: invalid token. Tokens are single-use and expire after 5 minutes.']
  except ldap.LDAPError, e:
    return [('Error: ' + e.message['desc'])]
  try:
    mod_ssha = [(ldap.MOD_REPLACE, 'userPassword', ssha)]
    cx.modify_s(userDN,mod_ssha)
    results.append('Updated userPassword (wiki)')
  except:
    results.append('Error updating userPassword (wiki)')
  try:
    mod_ntpw = [(ldap.MOD_REPLACE, 'sambaNTPassword', nt)]
    cx.modify_s(userDN,mod_ntpw)
    results.append('Updated sambaNTPassword (fileserver)')
  except:
    results.append('Error updating  sambaNTPassword')
  try:
    cx.unbind_s()
  except: 
    pass
  return results

def getEmail(uid):
  results = []
  userDN = 'uid=' + uid + ',' + baseDN
  try:
    cx = ldap.initialize(ldapURI)
    cx.simple_bind_s(adminDN,adminPw)
    mail = cx.search_s(userDN, ldap.SCOPE_SUBTREE, '(objectClass=ldgOrgPerson)', ['mail'])
    return mail[0][1]['mail'][0]
  except:
    return 

