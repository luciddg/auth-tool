# -*- coding: utf-8 -*-
import cherrypy
from jinja2 import Template
import ldap
import mock
from mockldap import MockLdap
import smtplib
import unittest

from lib.plugin.cpemail import EmailEnginePlugin
from lib.plugin.cpldap import LDAPEnginePlugin
from lib.plugin.passwd import PasswordEnginePlugin
from lib.plugin.template import Jinja2TemplatePlugin
from lib.plugin.token import TokenEnginePlugin

from tests.utils.cptestcase import BaseCherryPyTestCase
from tests.utils.ldap_data import LDAPTestDirectory
from tests.utils import Root

def setUpModule():
  cherrypy.tree.mount(Root(), '/')
  cherrypy.engine.start()
setup_module = setUpModule

def tearDownModule():
  cherrypy.engine.exit()
teardown_module = tearDownModule

class TestEmailPlugin(BaseCherryPyTestCase):


  @classmethod
  def setUpClass(cls):
    cherrypy.engine.stop()
    cherrypy.engine.email = EmailEnginePlugin(
        bus=cherrypy.engine,
        fromaddr="test@tester.com"
        )
    cherrypy.engine.email.subscribe()
    cherrypy.engine.start()

  @classmethod
  def tearDownClass(cls):
    cherrypy.engine.email.unsubscribe()
    del cherrypy.engine.email

  def setUp(self):
    self.smtp_patcher = mock.patch('smtplib.SMTP', return_value='smtp_connection')
    self.mock_smtp = self.smtp_patcher.start()

  def tearDown(self):
    del self.mock_smtp
    self.smtp_patcher.stop()
    del self.smtp_patcher

  @mock.patch('cherrypy.engine.publish',
              return_value=[
                'tokenabcdef0123456789',
                Template('{{ user.mail }}'),
                Template('{{ user.mail }}')
                ]
              )
  def test_send_reset_email(self, mock_bus):
    pass

  def test_send_username_email(self):
    pass

class TestLDAPPlugin(BaseCherryPyTestCase):

   
  @classmethod
  def setUpClass(cls):
    cls.mockldap = MockLdap(LDAPTestDirectory.directory)
    cherrypy.engine.stop()
    cherrypy.engine.ldap = LDAPEnginePlugin(
        bus=cherrypy.engine,
        uri="ldap://localhost/",
        base_dn="ou=example,o=test",
        bind_dn="cn=admin,ou=example,o=test",
        bind_pw="ldaptest",
        tls=True,
        no_verify=True)
    cherrypy.engine.ldap.subscribe()
    cherrypy.engine.start()

  @classmethod
  def tearDownClass(cls):
    cherrypy.engine.ldap.unsubscribe()
    del cherrypy.engine.ldap
    del cls.mockldap

  def setUp(self):
    self.mockldap.start()
    self.ldapobj = self.mockldap['ldap://localhost/']
    # hashes for password: changeme
    self.hashes = {
        'userPassword': '{SSHA}6QBuyak4WbsUzcqUKx0yB74RFUFvDbys',
        'sambaNTPassword': '6597D9FE8469E21D840E2CBFF8D43C8B',
        }

  def tearDown(self):
    del self.hashes
    self.mockldap.stop()
    del self.ldapobj

  def test_bad_base_dn(self):
    with self.assertRaises(cherrypy.process.wspbus.ChannelFailures):
      cherrypy.engine.publish('ldap-auth', 'alice,ou==bad,,', 'alicepw')
  
  def test_auth(self):
    auth = cherrypy.engine.publish('ldap-auth', 'alice', 'alicepw').pop()
    self.assertEqual(auth, True)
    with self.assertRaises(cherrypy.process.wspbus.ChannelFailures):
      cherrypy.engine.publish('ldap-auth', 'alice', 'bobpw')

  def test_get_user_by_uid(self):
    alice = cherrypy.engine.publish('ldap-user-by-uid', 'alice').pop()
    self.assertEqual(alice['uid'], 'alice')
    nouser = cherrypy.engine.publish('ldap-user-by-uid', 'nouser').pop()
    self.assertEqual(nouser, {})

  def test_get_user_by_email(self):
    bob = cherrypy.engine.publish('ldap-user-by-email', 'bob').pop()
    self.assertEqual(bob['mail'], 'bob@example.com')
    nouser = cherrypy.engine.publish('ldap-user-by-email', 'nouser').pop()
    self.assertEqual(nouser, {})

  def test_set_password(self):
    username = 'bob'
    cherrypy.engine.publish('ldap-set-password', username, self.hashes)
    bob = cherrypy.engine.publish('ldap-user-by-uid', 'bob').pop()
    self.assertEqual(self.hashes['userPassword'] in bob['userPassword'], True)
    self.assertEqual(self.hashes['sambaNTPassword'] in bob['sambaNTPassword'], True)
    self.assertEqual(cherrypy.engine.publish('ldap-auth', 'bob', 'changeme'), [True])

  def test_change_password(self):
    cherrypy.engine.publish('ldap-change-password', 'bob', 'bobpw', self.hashes)
    bob = cherrypy.engine.publish('ldap-user-by-uid', 'bob').pop()
    self.assertEqual(self.hashes['userPassword'] in bob['userPassword'], True)
    self.assertEqual(self.hashes['sambaNTPassword'] in bob['sambaNTPassword'], True)
    self.assertEqual(cherrypy.engine.publish('ldap-auth', 'bob', 'changeme'), [True])

  def test_change_passwd_bad_creds(self):
    with self.assertRaises(cherrypy.process.wspbus.ChannelFailures):
      cherrypy.engine.publish('ldap-change-password', 'bob', 'alicepw', self.hashes)

  def test_change_passwd_bad_dn(self):
    with self.assertRaises(cherrypy.process.wspbus.ChannelFailures):
      cherrypy.engine.publish('ldap-change-password', 'bob,,', 'alicepw', self.hashes)

  def test_add_sshpubkey(self):
    # key validation happens at the model level; using a short key for brevity
    sshpubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAo1d01QraTlMVSsbxNrRFi9wrf+M7Q== fakekey'
    cherrypy.engine.publish('ldap-add-key', 'bob', sshpubkey)
    bob = cherrypy.engine.publish('ldap-user-by-uid', 'bob').pop()
    self.assertEqual(sshpubkey in bob['sshPublicKey'], True)

  def test_delete_sshpubkey(self):
    sshpubkey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAo1d01QraTlMVSsbxNrRFi9wrf+M7Q== fakekey'
    cherrypy.engine.publish('ldap-delete-key', 'bob', sshpubkey)
    bob = cherrypy.engine.publish('ldap-user-by-uid', 'bob').pop()
    self.assertEqual(sshpubkey not in bob['sshPublicKey'], True)

class TestPasswdPlugin(BaseCherryPyTestCase):


  @classmethod
  def setUpClass(cls):
    cherrypy.engine.stop()
    cherrypy.engine.passwd = PasswordEnginePlugin(cherrypy.engine)
    cherrypy.engine.passwd.subscribe()
    cherrypy.engine.start()

  @classmethod
  def tearDownClass(cls):
    cherrypy.engine.passwd.unsubscribe()
    del cherrypy.engine.passwd

  @mock.patch('os.urandom', return_value='o\r\xbc\xac')
  def test_plugin(self, mock_random):
    print cherrypy.engine.publish
    hashes = cherrypy.engine.publish('password-hash', 'changeme').pop()
    self.assertIsInstance(hashes, dict)
    self.assertEqual(hashes['userPassword'], '{SSHA}6QBuyak4WbsUzcqUKx0yB74RFUFvDbys')
    self.assertEqual(hashes['sambaNTPassword'], '6597D9FE8469E21D840E2CBFF8D43C8B')

class TestTokenPlugin(BaseCherryPyTestCase):


  valid_token = 'e293ddd96cf57be2e93f481f944b11c644ef13161e20ad19e2c59ee0c311bed0'
  invalid_token = '0123456789abcef0123456789abcef'
  data = 'data'
  epoch = 16000.0

  @classmethod
  def setUpClass(cls):
    cherrypy.engine.stop()
    cherrypy.engine.token = TokenEnginePlugin(cherrypy.engine, secret="testsecret")
    cherrypy.engine.token.subscribe()
    cherrypy.engine.start()

  @classmethod
  def tearDownClass(cls):
    cherrypy.engine.token.unsubscribe()
    del cherrypy.engine.token

  @mock.patch('math.floor', return_value=epoch)
  def test_create_token(self, mock_epoch):
    token = cherrypy.engine.publish('token-gen', self.data).pop()
    self.assertEqual(token, self.valid_token)

  @mock.patch('math.floor', return_value=epoch)
  def test_valid_token(self, mock_epoch):
    valid = cherrypy.engine.publish('token-verify', self.valid_token, self.data).pop()
    self.assertEqual(valid, True)

  @mock.patch('math.floor', return_value=epoch)
  def test_invalid_token(self, mock_epoch):
    invalid = cherrypy.engine.publish('token-verify', self.invalid_token, self.data).pop()
    self.assertEqual(invalid, False)

  @mock.patch('math.floor', return_value=epoch)
  def test_invalid_data(self, mock_epoch):
    invalid = cherrypy.engine.publish('token-verify', self.valid_token, 'baddata').pop()
    self.assertEqual(invalid, False)

  def test_expired_token(self, mock_epoch=15999.0):
    invalid = cherrypy.engine.publish('token-verify', self.valid_token, self.data).pop()
    self.assertEqual(invalid, False)

