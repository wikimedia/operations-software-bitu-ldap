# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

import bituldap as b
from tests import config


class GroupTestCase(unittest.TestCase):
    def setUp(self) -> None:
        config.setup()

    def test_list_all(self):
        groups = b.list_groups()
        cns = [group.entry_dn for group in groups]
        self.assertIn('cn=www,ou=groups,dc=example,dc=org', cns)

    def test_create_group(self):
        created, group = b.new_group('suppliers', gid_number=9999)
        self.assertTrue(created)
        self.assertIsNotNone(group)
        self.assertEqual(group.gidNumber, 9999)
        self.assertEqual(b.next_gid_number(), 10000)

    def test_groups_by_user(self):
        dn = 'uid=acarr,ou=people,dc=example,dc=org'
        groups = b.member_of(dn)
        self.assertEqual(len(groups), 6)
        self.assertGreater(groups[0].gidNumber.value, 0)

    def test_add_remove_group_member(self):
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