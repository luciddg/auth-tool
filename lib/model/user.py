# -*- coding: utf-8 -*-

import cherrypy
from cherrypy.process.wspbus import ChannelFailures
from ldap import INVALID_CREDENTIALS

from lib.model.sshkey import SSHKey

__all__ = ['User']

class User(object):
  """
  An LDAP user with a dependency on the following
  objectClasses: posixAccount, ldapPublicKey
  """


  def __init__(self, username):
    self.auth = False

    user_attributes = cherrypy.engine.publish("ldap-user-by-uid", username).pop()

    if not user_attributes:
      if isinstance(user_attributes, dict):
        raise InvalidUser
      elif user_attributes is None:
        raise UserModelException
    else:
      # pop off known attributes to handle ldap search
      # result semantics

      # pylint: disable=CO103
      self.cn = user_attributes.pop('cn')[0]
      self.uid = user_attributes.pop('uid')[0]
      self.uidNumber = user_attributes.pop('uidNumber')[0]
      self.mail = user_attributes.pop('mail')[0]
      self.homeDirectory = user_attributes.pop('homeDirectory')[0]
      # pylint: enable=CO103

      if 'sshPublicKey' in user_attributes:
        self.sshPublicKey = [SSHKey(key) for key in user_attributes.pop('sshPublicKey')]

      # unpack the remaining attr/val pairs into instance vars
      for attr, val in user_attributes.items():
        setattr(self, attr, val)

  @staticmethod
  def get_by_uid(uid):
    """
    Lookup a user by its username and return the user record
    """
    try:
      user = cherrypy.engine.publish("ldap-user-by-uid", uid).pop()
    except ChannelFailures as exc:
      raise UserModelException(exc)

  @staticmethod
  def get_by_email(email):
    """
    Lookup a user by its email address and return the user record
    """
    try:
      user = cherrypy.engine.publish("ldap-user-by-email", email).pop()
      return user
    except ChannelFailures as exc:
      raise UserModelException(exc)

  def authenticate(self, password):
    """
    Attempt to bind as the user.  Set an instance varialbe indicating 
    success or failure.  Returns True or raises InvalidCredentials.
    """
    try:
      self.auth = cherrypy.engine.publish("ldap-auth", self.uid, password).pop()
      return True
    except ChannelFailures:
      raise InvalidCredentials

  def set_password(self, newpassword):
    """
    Obtain SSHA and NTPassword hashes for a given password,
    then administratively set the user's password.
    """
    hashes = cherrypy.engine.publish('password-hash', newpassword).pop()
    try:
      cherrypy.engine.publish('ldap-set-password', self.uid, hashes)
    except ChannelFailures as exc:
      raise UserModelException(exc)

  def change_password(self, oldpassword, newpassword):
    """
    Obtain SSHA and NTPassword hashes for a given password,
    then set the user's password using their own credentials.
    """
    hashes = cherrypy.engine.publish('password-hash', newpassword).pop()

    try:
      cherrypy.engine.publish('ldap-change-password', 
                              self.uid,
                              oldpassword,
                              hashes)
    except ChannelFailures as exc:
      if isinstance(exc.get_instances()[0], INVALID_CREDENTIALS):
        raise InvalidCredentials
      else:
        raise UserModelException(exc)

  def add_key(self, sshpubkey):
    """
    Add an SSH public key to the user's ldap record
    """
    try:
      cherrypy.engine.publish('ldap-add-key', self.uid, sshpubkey)
    except ChannelFailures as exc:
      raise UserModelException(exc)

  def delete_key(self, fingerprint):
    """
    Delete the matching (by fingerprint) ssh public key from
    the user's ldap record.
    """
    deletion_candidate = next((key for key in self.sshPublicKey if key.fingerprint == fingerprint), None)

    if deletion_candidate is None:
      raise UserModelException

    try:
      cherrypy.engine.publish('ldap-delete-key', self.uid, deletion_candidate.key)
    except ChannelFailures as exc:
      raise UserModelException(exc)

class UserModelException(Exception):
  """
  Base exception for the User class
  """
  pass

class InvalidUser(UserModelException):
  """
  User was not found in LDAP
  """
  pass

class InvalidCredentials(UserModelException):
  pass
