Configuration
===============

AuthTool uses the standard `CherryPy configuration mechanism`_.
In keeping with the standard, there are two configuration 
files included: server.cfg and app.cfg.

.. _CherryPy configuration mechanism: http://cherrypy.readthedocs.org/en/latest/basics.html#configuring

Server Configuration
--------------------

Nothing special here.  Refer to the `docs`_ for what we do here.

.. _docs: http://cherrypy.readthedocs.org/en/latest/config.html#global-config

Application Configuration
-------------------------

The application config consists of a few sections, each pertaining to a plugin 
or area of functionality within the application.

Branding
^^^^^^^^

.. code-block:: ini

   [branding]
   appname: "Password & Key Utility"
   domain: "example.com"

``appname``

The human readable name for the application.  
This overrides "AuthTool" as the name displayed in the web UI.

``domain``

When provided, adds functionality for input-group addons in the login forms.  
Also sets the default email domain so users aren't required to enter full email 
addresses for password resets or username reminders.

LDAP
^^^^

.. code-block:: ini

   [ldap]
   uri: "ldaps://ldap.example.com/"
   tls: True
   no_verify: False
   bind_dn: "cn=admin"
   bind_pw: "admin"
   base_dn: "ou=people,dc=example,dc=com"

``uri``

A valid LDAP url for the server.

``tls``

Negotiate TLS with the server.

``no_verify``

Don't perform certificate validation on TLS connections.
Sets :py:const:`OPT_X_TLS_REQUIRE_CERT` and :py:const:`OPT_X_TLS_NEVER` on the ldap library.

``bind_dn``

The administrative dn to bind as.  
This dn should have permissions to write password attributes.

``bind_pw``

The password for the above dn.

``base_dn``

The dn where users will be found.  
All searches are performed with a scope of :py:const:`ONE_LEVEL`, so be sure to set this accurately.

E-Mail
^^^^^^

.. code-block:: ini

   [email]
   html_template: "email.html"
   txt_template: "email.txt"

.. note::

  The templates will be passed the user object as its input.
  The :py:data:`cn`, :py:data:`reset_url`, :py:data:`uid`, and :py:data:`login_url` 
  attributes will be relvant to the templates.

``html_template``

A jinja templated html email template to be used in multi-part messaging 
for password resets and username reminders.

``txt_template``

A jinja templated plaintext email template to be used in multi-part messaging
for password resets and username reminders.

SMTP
^^^^

.. code-block:: ini

   [smtp]
   server: "localhost.com"
   port: 25
   user: "user"
   password: "password"
   from: "noreply@example.com"

``server``

The SMTP server to use to send email.

``port``

The port to connect to to send mail.

``user``

The optional user to authenticate as with the smtp server.  
If omitted, authentication is not used.

``password``

The password for the optional user.
If user is supplied, this is required.

``from``

The "from" address to send mail from.

Token
^^^^^

.. code-block:: ini

   [token]
   secret: "s3kuR1ty"
   expiry: 86400

``secret``

The secret to use to hash password reset tokens.

.. warning::

  Changing this invalidates all previously generated tokens.

``expiry``

The time, in seconds, to allow a token to exist.  Default is 86400 (24 hours).
