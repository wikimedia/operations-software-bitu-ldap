# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import patch

import bituldap as b
from tests import config


class GroupTestCase(unittest.TestCase):
    @patch("bituldap.create_connection", return_value=config.connect())
    def test_list_all(self, mock_connect):
        groups = b.list_groups()
        cns = [group.entry_dn for group in groups]
        self.assertIn('cn=www,ou=groups,dc=example,dc=org', cns)

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_create_group(self, mock_connect):
        user_dn = 'uid=lisa59,ou=people,dc=example,dc=org'
        self.assertEqual(b.next_gid_number(), 9001)
        created, group = b.new_group('suppliers',
                                     gid_number=9999,
                                     members=[user_dn])
        self.assertTrue(created)
        self.assertIsNotNone(group)
        self.assertEqual(group.gidNumber, 9999)
        self.assertEqual(len(group.member), 1)
        self.assertEqual(group.member[0], user_dn)
        self.assertEqual(b.next_gid_number(), 10000)

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_create_group_no_members(self, mock_connect):
        # Groups must have members. Check that group creation fails
        # on an empty set of users.
        created, group = b.new_group('farms', gid_number=10000, members=[])
        self.assertFalse(created)
        groups = b.list_groups()
        cns = [group.entry_dn for group in groups]
        self.assertNotIn('cn=farms,ou=groups,dc=example,dc=org', cns)

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_groups_by_user(self, mock_connect):
        dn = 'uid=acarr,ou=people,dc=example,dc=org'
        groups = b.member_of(dn)
        self.assertEqual(len(groups), 6)
        self.assertGreater(groups[0].gidNumber.value, 0)

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_add_remove_group_member(self, mock_connect):
        user = b.get_user('acarr')
        group = b.get_group('accounting')
        self.assertNotIn(user.entry_dn, group.member)

        members_start = group.member.values

        member_count = len(group.member)

        group.member.add(user.entry_dn)
        self.assertTrue(group.entry_commit_changes())
        del group

        group = b.get_group('accounting')
        members_end = group.member.values
        diff = set(members_end) - set(members_start)
        self.assertIn(user.entry_dn, group.member)
        self.assertEqual(member_count +1 , len(group.member))
        self.assertEqual(set(['uid=acarr,ou=people,dc=example,dc=org',]), diff)

        group.member.delete(user.entry_dn)
        self.assertTrue(group.entry_commit_changes())
        del group
        group = b.get_group('accounting')
        self.assertEqual(member_count, len(group.member))