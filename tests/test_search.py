# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

import bituldap as b

from ldap3 import Server
from tests import config

class SearchTestCase(unittest.TestCase):
    def setUp(self):
        config.setup()

    def test_group_search(self):
        group = b.get_group('www')
        self.assertEqual(group.entry_dn, 'cn=www,ou=groups,dc=example,dc=org')

    def test_user(self):
        user = b.get_user('eduncan')
        self.assertEqual(user.entry_dn, 'uid=eduncan,ou=people,dc=example,dc=org')
        self.assertEqual(user.loginShell, '/bin/csh')
