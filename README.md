Lucid Password & SSH Key Utility
================================

Provides a web interface for password change/recovery and SSH key 
management for Lucid's LDAP infrastructure.

Development
-----------

* Clone this repository
* Install dependencies from the `requirements.txt`
* Start the local webserver.
  `python passmgr/controller.py`

Running tests
-------------

Tests are intended to be run with `nose`.  Simply run:

```
nosetests
```

Code coverage html output will be in `cover/`
