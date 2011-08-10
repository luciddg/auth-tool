import ldap
from lib import sha
import smbpasswd

ldapURI = 'ldap://localhost'
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
    return e.message['desc']

def passwd(uid,newpw,oldpw=''):
  results = []
  ssha = sha.passwd(newpw)
  nt = smbpasswd.nthash(newpw)
  userDN = 'uid=' + uid + ',' + baseDN
  try:
    cx = ldap.initialize(ldapURI)
    if oldpw:
      cx.simple_bind_s(userDN,oldpw)
    else:
      cx.simple_bind_s(adminDN,adminPw)
  except ldap.LDAPError, e:
    results.append(e.message['desc'])
    return results
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

