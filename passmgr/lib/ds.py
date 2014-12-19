import base64
import hashlib
import ldap
import smbpasswd
import struct

import sha
import tokenlib


ldapURI = 'ldap://10.11.12.10'
baseDN = 'ou=people,dc=luciddg,dc=com'
adminDN = 'uid=passmgr,dc=luciddg,dc=com'
adminPw = '3WT|78XoQ'

def authenticate(uid, password):
  cx = ldap.initialize(ldapURI)
  dn = 'uid=' + uid + ',' + baseDN
  try:
    cx.simple_bind_s(dn, password)
    cx.unbind_s()
    return 1
  except ldap.LDAPError, e:
    if 'desc' in e.message:
      error = 'Error: ' + e.message['desc']
    else:
      error = e
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

def getKeys(uid):
  '''
  Returns a list of ssh key strings in RFC4253 format for a given ldap user.
  '''

  userDN = 'uid=' + uid + ',' + baseDN

  try:
    cx = ldap.initialize(ldapURI)
    cx.simple_bind_s()
    results = cx.search_s(userDN, 
              ldap.SCOPE_SUBTREE, 
              '(objectClass=ldapPublicKey)', 
              ['sshPublicKey'])
    return results[0][1].get('sshPublicKey', [])
  except ldap.LDAPError, e:
    if 'desc' in e.message:
      error = 'Error: ' + e.message['desc']
    else:
      error = e
    return error

def fingerprint(key):
  '''
  Returns a  a triple containing key type, key fingerprint, and comment string from an 
  RFC4253 formatted public key.  Key is validated before fingerprint attempt.

  Returns None for an invalid key.
  '''

  if validateKey(key):
    key_type = key.strip().split()[0]
    b64d_key = base64.b64decode(key.strip().split()[1].encode('ascii'))
    comment = key.strip().split()[2].encode('ascii')

    fp_plain = hashlib.md5(b64d_key).hexdigest()
    fp_delim = ":".join (a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))

    fingerprint = (key_type, fp_delim, comment)

    return fingerprint
  else:
    return None

def validateKey(key):
  '''
  Validates a RFC4253 ssh public key of type ssh-rsa or ssh-dss.

  Checks that the data portion of the key can be base64 decoded and the
  header (first 4 bytes) is '7'.
  '''

  try:
    key_type, key_string, comment = key.split()

    data = base64.decodestring(key_string)
    str_len = struct.unpack('>I', data[:4])[0]
    data[4:4 + str_len] == key_type
  except:
    return False
  else:
    return True

def addKey(uid, key):
  '''
  Add an ssh pub key to a user's ldap record
  '''

  userDN = 'uid=' + uid + ',' + baseDN
  status = 'success'
  
  try:
    cx = ldap.initialize(ldapURI)
    cx.simple_bind_s(adminDN,adminPw)
    modlist = [(ldap.MOD_ADD, 'sshPublicKey', key)]
    cx.modify_s(userDN, modlist)
    msg = 'key added successfully'
  except ldap.LDAPError, e:
    status = 'error'
    if 'desc' in e.message:
      msg = e.message['desc']
    else:
      msg = e

  return status, msg

def rmKey(uid, key_fp):
  '''
  Find and remove an ssh pub key from a user's ldap record
  '''

  userDN = 'uid=' + uid + ',' + baseDN
  status = 'success'

  try:
    cx = ldap.initialize(ldapURI)
    cx.simple_bind_s(adminDN,adminPw)

    for key in getKeys(uid):
      ldapKeyFp = fingerprint(key)
      if ldapKeyFp is not None:

        if ldapKeyFp[1] == key_fp:
          modlist = [(ldap.MOD_DELETE, 'sshPublicKey', key)]
          cx.modify_s(userDN, modlist)
          msg = 'Removed key: {0}'.format(key_fp)
          break

    else:
      status = 'error'
      msg = "Unable to find key: {0}".format(key_fp)
  except ldap.LDAPError, e:
    status = 'error'
    if 'desc' in e.message:
      msg = e.message['desc']
    else:
      msg = e

  return status, msg
