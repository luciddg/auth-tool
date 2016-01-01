AuthTool
========
.. image:: https://travis-ci.org/luciddg/auth-tool.svg?branch=master
   :target: https://travis-ci.org/luciddg/auth-tool

AuthTool is a self-service password reset and SSH public key management application for OpenLDAP directories. 

Features include:

* Forgotten passwords can be reset using a token sent by email.
* Forgotten username reminders can be sent by email.
* Passwords can be changed using the current password.
* SSH public keys can be validated and added or deleted.

Prerequisites
-------------

This application makes many assumptions about your LDAP server's configuration and schema.

LDAP Schema
^^^^^^^^^^^

* The `sshPublicKey`_ schema from the `openssh-ldap-publickey`_ project.
* The ``posixUser`` objectClass
* The ``sambaSamAccount`` objectClass

.. _sshPublicKey: https://github.com/AndriiGrytsenko/openssh-ldap-publickey/blob/master/misc/openssh-lpk-openldap.schema
.. _openssh-ldap-publickey: https://github.com/AndriiGrytsenko/openssh-ldap-publickey

LDAP Configuration
^^^^^^^^^^^^^^^^^^

This application assumes anonymous binds are permitted for obtaining limited user information.
A service account is used for administrative operations such as setting passwords.

Running AuthTool
----------------

You can run AuthTool in two supported ways:  Docker and locally.  
Both use the same interface, so it comes down to personal preference.

Docker
^^^^^^

A Dockerfile is included to build and run the application.

Local
^^^^^

This application is meant to use the internal CherryPy server.  Therefore, it can simply be run using the provided module:

`python serve.py`

