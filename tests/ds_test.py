# -*- coding: utf-8 -*-

import ldap
import unittest

from mock import Mock, patch
from mockldap import MockLdap

from passmgr.lib import ds

class DsTestCase(unittest.TestCase):
  '''
  Test functionality in the DirectoryServices module.
  '''

  ldapUri = 'ldap://localhost/'

  top = ('o=test', { 'o': 'test'})
  example = ('ou=example,o=test', {'ou': 'example'})
  admin = ('cn=admin,ou=example,o=test', {'cn': 'admin', 'userPassword': ['ldaptest']})
  alice = ('uid=alice,ou=example,o=test', {'cn': 'alice', 'userPassword': ['alicepw']})
  bob = ('uid=bob,ou=example,o=test', {'cn': 'bob',
    'userPassword': ['bobpw'],
    'sshPublicKey': ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyhfZdZUjJuD8fFdYsKvPSMUgUahjxCp50BbT2sxRwE+9ij5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/MIWwcUGg3fv2UTKwhU7cWflVjxkVEtG2OYImI1jQfYs/sSD2BcmagXwZxBzPHLuu/zSLh/OzJYcf9RKR4t2AgQqpx5g9A0SVw1R/we4Cpm7MmGaNjxif0pBS/BWTxJ bob@example.test',
                     'ssh-dss AAAAB3NzaC1kc3MAAACBAKDBr7RQkFHQd95FGW3dMV7Rxc/IW2m2iDhVg1fDrHPfeQdV2IezMNgp7JWq4e94STSuyxUdr3gngXVamxeMUnnigIY92NjU4g971IPF2ttuHBQpaMs7rcnZZJl73X9xJZ2yHtwR+x/ey9QmeKwVis7GY5VECG2w+j7WP6HV4HZNAAAAFQDgvtc4zanxvJdc5pFgFudzE37jLQAAAIEAkY+b69evVzvjbzc8z+RjHeeFD2wvITXMCNmqYue2i1DSDHyyuX8MhU0QxlV2q9XtgEQ+PJPqIkGo+9PDFBXok/a/FXlHV0rJCuO/CnSOmiCadcrdlKEIPY/QyPxNwbbARHBfXpfWWQvsTqhbWAx+/+A2ITWqxGgdfcudj92m8P4AAACADvigz/c7xx8wqmAddLEDc3ODnfjOE6KVxBsr0eckr34ccpHGXtCDZkQLlBFbXvHet+kMzGj/udm/XqJi5o638PnD2MoVEJMiylDpvw0idEuJcfAMHvK92IC/hmXk3OQRFnHtpGohCL31MBfoVrXYM3IiM/SCFYHq5CEjRsETlqE= bob@example.test']})
  baduser = ('uid=baduser,ou=example,o=test', {'cn': 'baduser',
    'userPassword': ['baduserpw'],
    'sshPublicKey': ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyhfZdZUjJuD8fFdYsKvPSMUgUahjxCp50BbT2sxRwE+9ij5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/MIWwcUGg3',
                     'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZeHe71ej4gNwhwFrLMn7OY5UNMpCGII9pNJZ+gtHjBZ5cT8mzwSDqbOG3/yeQyj5QukZAJCG2ggM9TcEx9sFWMk1IDT72u0AOjKeYcImfAm/4Z0PcH6ozlUjyfJspb7LG5fxxkuxVdOQ6ZWWHxA7Ckf4JzxCVxmbVDl2BAC98t/ badkey@example.test']})

  directory = dict([top, example, admin, alice, bob, baduser])

  @classmethod
  def setUpClass(cls):
    cls.mockldap = MockLdap(cls.directory)

  @classmethod
  def tearDownClass(cls):
    del cls.mockldap

  def setUp(self):
    '''Patch ldap.initialize'''
    self.mockldap.start()
    self.ldapobj = self.mockldap[self.ldapUri]

  def tearDown(self):
    '''reset state and stop patching ldap.initialize'''
    self.mockldap.stop()
    del self.ldapobj

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  def testAuthenticationSuccess(self):
    '''Test ldap authentication success''' 
    self.assertEqual(ds.authenticate('bob', 'bobpw'), 1)
    self.assertEqual(self.ldapobj.methods_called(), 
        ['initialize', 'simple_bind_s', 'unbind_s'])

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  def testAuthenticationFailure(self):
    '''Test ldap authentication failure with bad user''' 
    self.assertIsInstance(ds.authenticate('nouser', 'nopass'),
        ldap.LDAPError)
    self.assertEqual(self.ldapobj.methods_called(), 
        ['initialize', 'simple_bind_s'])

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  def testGetKeysValidUser(self):
    '''Test getting sshPublicKeys for valid ldap user with keys'''
    self.ldapobj.search_s.seed('uid=bob,ou=example,o=test', 
        ldap.SCOPE_SUBTREE, 
        '(objectClass=ldapPublicKey)',
        ['sshPublicKey']
        )([self.bob])
    self.assertListEqual(ds.getKeys('bob'), self.bob[1]['sshPublicKey'])
    self.assertEqual(self.ldapobj.methods_called(), 
        ['initialize', 'simple_bind_s', 'search_s'])

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  def testGetKeysValidUserNoKeys(self):
    '''Test getting sshPublicKeys for valid ldap user with no keys'''
    self.ldapobj.search_s.seed('uid=alice,ou=example,o=test', 
        ldap.SCOPE_SUBTREE, 
        '(objectClass=ldapPublicKey)',
        ['sshPublicKey']
        )([self.alice])
    self.assertListEqual(ds.getKeys('alice'), [])
    self.assertEqual(self.ldapobj.methods_called(), 
        ['initialize', 'simple_bind_s', 'search_s'])

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  def testGetKeysInvalidUser(self):
    '''Test getting sshPublicKeys for invalid ldap user'''
    self.assertIsInstance(ds.getKeys('nouser'), ldap.LDAPError)

  def testFingerprintValidKey(self):
    '''Test fingerprinting a valid ssh pubkey'''
    self.assertEqual(ds.fingerprint(self.bob[1]['sshPublicKey'][1]),
      ('ssh-dss', 'b5:27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e', 'bob@example.test'))

  def testFingerprintInvalidKey(self):
    '''Test fingerprinting an invalid ssh pubkey'''
    self.assertIsNone(ds.fingerprint(self.bob[1]['sshPublicKey'][1][25:50]))

  def testValidateKeySuccess(self):
    '''Test that a valid key is indeed valid'''
    self.assertTrue(ds.validateKey(self.bob[1]['sshPublicKey'][1]))

  def testValidateKeySuccess(self):
    '''Test that an invalid key is indeed invalid'''
    self.assertFalse(ds.validateKey(self.bob[1]['sshPublicKey'][1][25:50]))
      
  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  @patch('passmgr.lib.ds.adminDN', 'cn=admin,ou=example,o=test')
  @patch('passmgr.lib.ds.adminPw', 'ldaptest')
  def testAddKeyValidUser(self):
    '''Test adding a key to a valid ldap user'''
    self.assertEqual(ds.addKey('bob', self.bob[1]['sshPublicKey'][1]), 
        ('success', 'key added successfully'))

  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  @patch('passmgr.lib.ds.adminDN', 'cn=admin,ou=example,o=test')
  @patch('passmgr.lib.ds.adminPw', 'ldaptest')
  def testAddKeyInvalidUser(self):
    '''Test adding a key to an invalid ldap user'''
    self.assertEqual(ds.addKey('nouser', self.bob[1]['sshPublicKey'][1])[0], 
        'error')
    self.assertIsInstance(ds.addKey('nouser', self.bob[1]['sshPublicKey'][1])[1], 
        ldap.LDAPError)

  @patch('passmgr.lib.ds.getKeys')
  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  @patch('passmgr.lib.ds.adminDN', 'cn=admin,ou=example,o=test')
  @patch('passmgr.lib.ds.adminPw', 'ldaptest')
  def testRmKeyValidUser(self, getKeys):
    '''Test removing key from valid user'''
    getKeys.return_value = self.bob[1]['sshPublicKey']
    self.assertEqual(ds.rmKey('bob', 'b5:27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'),
        ('success', 'Removed key: b5:27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'))

  @patch('passmgr.lib.ds.getKeys')
  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  @patch('passmgr.lib.ds.adminDN', 'cn=admin,ou=example,o=test')
  @patch('passmgr.lib.ds.adminPw', 'ldaptest')
  def testRmKeyValidUserInvalidKey(self, getKeys):
    '''Test removing key from valid user with an invalid key'''
    self.assertEqual(ds.rmKey('bob', '27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'),
        ('error', 'Unable to find key: 27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'))

  @patch('passmgr.lib.ds.getKeys')
  @patch('passmgr.lib.ds.baseDN', 'ou=example,o=test')
  @patch('passmgr.lib.ds.ldapURI', 'ldap://localhost/')
  @patch('passmgr.lib.ds.adminDN', 'cn=admin,ou=example,o=test')
  @patch('passmgr.lib.ds.adminPw', 'ldaptest')
  def testRmKeyInvalidUser(self, getKeys):
    '''Test removing key from an invalid user'''
    getKeys.return_value = []
    self.assertEqual(ds.rmKey('nouser', 'b5:27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'),
        ('error', 'Unable to find key: b5:27:8d:7f:5e:79:b5:7c:3c:87:02:d5:6b:ad:53:4e'))
