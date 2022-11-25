# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from ldap3 import Server
from ldap3.core.exceptions import LDAPEntryAlreadyExistsResult
import bituldap as b


class UserTestCase(unittest.TestCase):
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


    def test_user_create(self):
        uid = 'bobcat'
        user = b.new_user(uid)
        self.assertIsNotNone(user)

        user.uidNumber = b.next_uid_number()
        user.gidNumber = 2000
        user.homeDirectory = f'/home/{uid}'
        user.sn = 'Bob'
        user.givenName = 'Cat'
        user.entry_commit_changes()

    def test_user_update(self):
        user = b.get_user('acarr')
        self.assertNotEqual(user.loginShell, '/bin/ksh')

        user.loginShell = '/bin/ksh'
        self.assertTrue(user.entry_commit_changes())
        del(user)

        user = b.get_user('acarr')
        self.assertEqual(user.loginShell, '/bin/ksh')


    def test_uid_conflict(self):
        uid_number = b.next_uid_number()

        # Create user 1
        uid1 = 'cmahoney'
        user1= b.new_user(uid1)
        self.assertIsNotNone(user1)

        user1.uidNumber = uid_number
        user1.gidNumber = 2000
        user1.homeDirectory = f'/home/{uid1}'
        user1.sn = 'Carey'
        user1.givenName = 'Mahoney'

        # Create user 2
        uid2 = 'etackleberry'
        user2= b.new_user(uid2)
        self.assertIsNotNone(user2)

        user2.uidNumber = uid_number
        user2.gidNumber = 2000
        user2.homeDirectory = f'/home/{uid2}'
        user2.sn = 'Eugene'
        user2.givenName = 'Tackleberry'

        # Commit both new users, with identical uid numbers.
        # Only the first should succeed, the other should
        # return False.
        self.assertTrue(user1.entry_commit_changes())
        self.assertFalse(user2.entry_commit_changes())
