# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

import bituldap as b


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        users = b.types.LdapQueryOptions(
            'ou=people,dc=example,dc=org',
            ['inetOrgPerson'], ['posixAccount'])

        groups = b.types.LdapQueryOptions(
            'ou=groups,dc=example,dc=org',
            ['groupOfNames'], ['posixGroup'])

        b.singleton.shared_configuration = b.types.Configuration(
            'localhost', 1389, 'cn=admin,dc=example,dc=org',
            'adminpassword', False, False, users, groups)

    def test_group_search(self):
        group = b.get_group('www')
        self.assertEqual(group.entry_dn, 'cn=www,ou=groups,dc=example,dc=org')

    def test_user(self):
        user = b.get_user('eduncan')
        self.assertEqual(user.entry_dn, 'uid=eduncan,ou=people,dc=example,dc=org')
        self.assertEqual(user.loginShell, '/bin/csh')
