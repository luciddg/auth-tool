# -*- coding: utf-8 -*-

import cherrypy
from cherrypy.process import wspbus, plugins
from contextlib import contextmanager
import ldap

__all__ = ['LDAPEnginePlugin']

class LDAPEnginePlugin(plugins.SimplePlugin):
  """
  The plugin is registered to the CherryPy engine and therefore
  is part of the bus (the engine *is* a bus) registery.

  We use this plugin to create the LDAP connection.
  """


  def __init__(self, bus, uri, base_dn, bind_dn, bind_pw, tls=True, no_verify=False):
    plugins.SimplePlugin.__init__(self, bus)
    self.uri = uri
    self.base_dn = base_dn
    self.bind_dn = bind_dn
    self.bind_pw = bind_pw
    self.tls = tls
    self.no_verify = no_verify

  def start(self): # pragma: no cover
    self.bus.log('Starting LDAP plugin')
    self.bus.subscribe("ldap-auth", self.auth)
    self.bus.subscribe("ldap-user-by-email", self.get_user_by_email)
    self.bus.subscribe("ldap-user-by-uid", self.get_user_by_uid)
    self.bus.subscribe("ldap-set-password", self.set_password)
    self.bus.subscribe("ldap-change-password", self.change_password)
    self.bus.subscribe("ldap-delete-key", self.delete_sshpubkey)
    self.bus.subscribe("ldap-add-key", self.add_sshpubkey)

  def stop(self): # pragma: no cover
    self.bus.log('Disabling LDAP plugin')
    self.bus.unsubscribe("ldap-auth", self.auth)
    self.bus.unsubscribe("ldap-user-by-email", self.get_user_by_email)
    self.bus.unsubscribe("ldap-user-by-uid", self.get_user_by_uid)
    self.bus.unsubscribe("ldap-set-password", self.set_password)
    self.bus.unsubscribe("ldap-change-password", self.change_password)
    self.bus.unsubscribe("ldap-delete-key", self.delete_sshpubkey)
    self.bus.unsubscribe("ldap-add-key", self.add_sshpubkey)
    self.uri = None
    self.base_dn = None
    self.bind_dn = None
    self.bind_pw = None
    self.tls = None
    self.no_verify = None

  @contextmanager
  def _ldap_connection(self):
    """
    Context manager for ldap connections
    """
    if self.no_verify:
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,
                      ldap.OPT_X_TLS_NEVER)

    ldap_cxn = ldap.initialize('{0}'.format(self.uri))
    ldap_cxn.protocol_version = 3
    ldap_cxn.set_option(ldap.OPT_REFERRALS, 0)

    if self.tls and not self.uri.startswith('ldaps'):
      ldap_cxn.start_tls_s()

    yield ldap_cxn

  def _search(self, filterstr, attrlist=None):
    """
    A wrapper for the `LDAPObject.search_s` functionality.

    Perform an LDAP search operation, starting at the configured base DN.
    The filterstr argument is a string representation of the filter to
    apply in the search.  The retrieved attributes can be limited with the
    attrlist parameter.  If attrlist is None, all the attributes of each
    entry are returned.
    """
    with self._ldap_connection() as ldap_cxn:
      results = ldap_cxn.search_s(self.base_dn, ldap.SCOPE_ONELEVEL, filterstr, attrlist)
    return results

  def auth(self, username, password):
    """
    Authenticate a user against the ldap server
    """
    dn = 'uid={0},{1}'.format(username, self.base_dn)
    try:
      with self._ldap_connection() as ldap_cxn:
        ldap_cxn.simple_bind_s(dn, password)
      return True
    except ldap.INVALID_CREDENTIALS:
      raise
    except ldap.INVALID_DN_SYNTAX:
      self.bus.log('Invalid DN syntax in configuration: {0}'.format(self.base_dn), 40)
      raise
    except ldap.LDAPError as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def get_user_by_uid(self, uid):
    """
    Lookup an ldap user by uid and return a dict with
    all known and anonymously accessible attributes.
    """
    filter = '(uid={0})'.format(uid)
    try:
      user = self._search(filter)
      if not user or len(user) > 1:
        return {}
      else:
        return user[0][1]
    except ldap.LDAPError as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def get_user_by_email(self, email_address):
    """
    Lookup an ldap user by email address and return a dict with
    all known and anonymously accessible attributes.
    """
    filter = '(mail={0})'.format(email_address)
    try:
      user = self._search(filter)
      if not user or len(user) > 1:
        return {}
      else:
        return user[0][1]
    except ldap.LDAPError as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def set_password(self, username, hashes):
    """
    Administratively set the user's password using the given hashes.
    """
    dn = 'uid={0},{1}'.format(username, self.base_dn)
    try:
      with self._ldap_connection() as ldap_cxn:
        ldap_cxn.simple_bind_s(self.bind_dn, self.bind_pw)

        mod_nt = (ldap.MOD_REPLACE, 'sambaNTPassword', hashes['sambaNTPassword'])
        mod_ssha = (ldap.MOD_REPLACE, 'userPassword', hashes['userPassword'])
        mod_list = [mod_nt, mod_ssha]

        ldap_cxn.modify_s(dn, mod_list)

    except ldap.INVALID_CREDENTIALS:
      self.bus.log('Invalid credentials for admin user: {0}'.format(self.bind_dn), 40)
      raise
    except ldap.INSUFFICIENT_ACCESS:
      self.bus.log('Insufficient access for admin user: {0}'.format(self.bind_dn), 40)
      raise
    except ldap.INVALID_DN_SYNTAX:
      self.bus.log('Invalid DN syntax in configuration: {0}'.format(self.base_dn), 40)
      raise
    except ldap.LDAPError as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def change_password(self, username, oldpassword, hashes):
    """
    Change the user's password using their own credentials.
    """
    dn = 'uid={0},{1}'.format(username, self.base_dn)

    try:
      with self._ldap_connection() as ldap_cxn:
        ldap_cxn.simple_bind_s(dn, oldpassword)

        # don't use LDAPObject.passwd_s() here to make use of
        # ldap's atomic operations.  IOW, don't change one password
        # but not the other.
        mod_nt = (ldap.MOD_REPLACE, 'sambaNTPassword', hashes['sambaNTPassword'])
        mod_ssha = (ldap.MOD_REPLACE, 'userPassword', hashes['userPassword'])
        mod_list = [mod_nt, mod_ssha]
        ldap_cxn.modify_s(dn, mod_list)

    except ldap.INVALID_CREDENTIALS:
      raise
    except ldap.INVALID_DN_SYNTAX:
      self.bus.log('Invalid DN syntax in configuration: {0}'.format(self.base_dn), 40)
      raise
    except ldap.LDAPError as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def add_sshpubkey(self, username, sshpubkey):
    """
    Add an sshPublicKey attribute to the user's dn
    """
    dn = 'uid={0},{1}'.format(username, self.base_dn)

    try:
      with self._ldap_connection() as ldap_cxn:
        ldap_cxn.simple_bind_s(self.bind_dn, self.bind_pw)
        mod_list = [(ldap.MOD_ADD, 'sshPublicKey', str(sshpubkey))]
        ldap_cxn.modify_s(dn, mod_list)

    except (ldap.INVALID_CREDENTIALS, ldap.INSUFFICIENT_ACCESS, ldap.LDAPError) as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise

  def delete_sshpubkey(self, username, sshpubkey):
    """
    Add an sshPublicKey attribute to the user's dn
    """
    dn = 'uid={0},{1}'.format(username, self.base_dn)

    try:
      with self._ldap_connection() as ldap_cxn:
        ldap_cxn.simple_bind_s(self.bind_dn, self.bind_pw)
        mod_list = [(ldap.MOD_DELETE, 'sshPublicKey', str(sshpubkey))]
        ldap_cxn.modify_s(dn, mod_list)

    except (ldap.INVALID_CREDENTIALS, ldap.INSUFFICIENT_ACCESS, ldap.LDAPError) as e:
      self.bus.log('LDAP Error: {0}'.format(e.message['desc'] if 'desc' in e.message else str(e)),
                   level=40,
                   traceback=True)
      raise
