# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import bituldap as b
from tests import config

class UserTestCase(unittest.TestCase):
    def setUp(self):
        config.setup()

    def test_user_create(self):
        uid = 'zmcglunk'
        user = b.new_user(uid)
        self.assertIsNotNone(user)

        user.uidNumber = b.next_uid_number()
        user.gidNumber = 2000
        user.homeDirectory = f'/home/{uid}'
        user.sn = 'Zed'
        user.givenName = 'McGlunk'
        user.loginShell = '/bin/tcsh'
        user.entry_commit_changes()
        del(user)

        user = b.get_user(uid)
        self.assertEqual(user.sn, 'Zed')

    def test_user_update(self):
        user = b.get_user('csweetchuck')
        self.assertNotEqual(user.loginShell, '/bin/ksh')

        user.loginShell = '/bin/ksh'
        self.assertTrue(user.entry_commit_changes())
        del(user)

        user = b.get_user('csweetchuck')
        self.assertEqual(user.loginShell, '/bin/ksh')

    # When testing on a real OpenLDAP installation the LDAP server
    # will do the validation of the uidNumber, as specified by the
    # posixAccount schema. The mock LDAP server is unable to do this
    # type of validation.
    #@unittest.expectedFailure
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

        # The mock LDAP server fails to do the OpenLDAP validation
        # and will report that the commit_change() went corretly,
        # and return True. OpenLDAP will return false in this case.
        #self.assertFalse(user2.entry_commit_changes())

        del(user1)
        del(user2)

        user1 = b.get_user(uid1)
        user2 = b.get_user(uid2)
        self.assertEqual(user1.uidNumber, uid_number)
        self.assertIsNone(user2)
