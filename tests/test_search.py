# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

import bituldap as b

from ldap3 import Server

class SearchTestCase(unittest.TestCase):
    def setUp(self):
        users = b.types.LdapQueryOptions(
            'ou=people,dc=example,dc=org',
            ['inetOrgPerson'], ['posixAccount'])

        groups = b.types.LdapQueryOptions(
            'ou=groups,dc=example,dc=org',
            ['groupOfNames'], ['posixGroup'])

        server = Server(host='localhost', port=1389, use_ssl=False)
        b.singleton.shared_configuration = b.types.Configuration(
            servers=[server],
            username='cn=admin,dc=example,dc=org',
            password='adminpassword',
            read_only=False,
            users=users,
            groups=groups)

    def test_group_search(self):
        group = b.get_group('www')
        self.assertEqual(group.entry_dn, 'cn=www,ou=groups,dc=example,dc=org')

    def test_user(self):
        user = b.get_user('eduncan')
        self.assertEqual(user.entry_dn, 'uid=eduncan,ou=people,dc=example,dc=org')
        self.assertEqual(user.loginShell, '/bin/csh')
