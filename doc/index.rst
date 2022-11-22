.. Bitu LDAP documentation master file, created by
   sphinx-quickstart on Wed Sep  7 13:35:18 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bitu LDAP's documentation
=========================
The Bitu LDAP library will attempt to automatically setup a connection
to an LDAP server, using one of three methods, in the following order:

1. django settings file.
2. configuration file.
3. enviroment variables.


Configuration using Django
--------------------------------------------
Bitu LDAP will expect to find a dictionary in the
Django settings file, as the variable: **BITU_LDAP**.
The following is an example configuration, containing
the default values. For multiple servers, the URIs
entry can also be a list of URIs.

Notes on multiple servers (ServerPool): This is a
feature of the underlying ldap3 library. The default
pooling strategy is FIRST, meaning that the first
"active" server in the pool is used. See the ldap3
documentation for more information:
https://ldap3.readthedocs.io/en/latest/server.html#server-pool
It is currently not possible to configure Bitu-LDAP
to use a different HA strategy.

.. code-block:: python

   BITU_LDAP = {
      uri: 'ldaps://ldap.example.org',
      username: '',
      password: '',
      read_only: False,
      connection_timeout: 5,
      users: {
         dn: 'ou=users,dc=example,dc=org'
         object_classes: ['inetOrgPerson']
         auxiliary_classes: []
      }
      groups: {
         dn: 'ou=users,dc=example,dc=org'
         object_classes: ['groupOfNames']
         auxiliary_classes: []
      }
   }

Configuration using a configuration file
----------------------------------------
If the configuration file is found, and contains a valid
JSON object, this will be used as the connection parameters for
LDAP. The format is identical to the Django example.

By default the Bitu-LDAP library will search for configuration
file in the following locations, and in this order:
* Path, as defined by the environment variable: BITU_LDAP_CONFIG.
* .bituldap.json in the users home directory.
* /etc/bitu/ldap.config

When using the library as part of another project, additional
configuration file paths can be supplied to the function:

.. code-block:: python

   bituldap.configure.file()

Configuration using environment varaibles
-----------------------------------------
Failing to configure the LDAP connection using either Django or
a configuration file, Bitu-LDAP will fallback to environment
variables. Bitu-LDAP can be configured using the following variables.

BITU_LDAP_URI
   URI of the LDAP server, e.g. ldaps://ldap.example.org:686. Multiple
   URIs can be separated by spaces. If the first server in the list is
   active that server will always be used. See the server pool documentation
   for ldap3 for more information:
   https://ldap3.readthedocs.io/en/latest/server.html#server-pool

BITU_LDAP_READONLY
   Read only connection, True or False, defaults to True.

BITU_CONNECTION_TIMEOUT
   Timeout for establishing a connection to LDAP server.

BITU_USERNAME
   LDAP user, default: cn=admin,dc=example,dc=org

BITU_PASSWORD
   LDAP user password.

BITU_USER_DN
   Location of the LDAP user objects, default: ou=users,dc=example,dc=org

BITU_USER_CLASSES
   Comma separated list of object classes to apply to user objects, default: inetOrgPerson.

BITU_USER_AUX
   Comma separated list auxiliary classes to apply to user objects, default: ''.

BITU_GROUP_DN
   Location of the LDAP group objects, default: ou=group,dc=example,dc=org.

BITU_GROUP_CLASSES
   Comma separated list of object classes to apply to group objects, default: groupOfNames.

BITU_GROUP_AUX
   Comma separated list auxiliary classes to apply to group objects, default: ''.

Bitu LDAP modules
=================
.. toctree::
   :maxdepth: 2

   bituldap
   configuration
   types


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
