# SPDX-License-Identifier: GPL-3.0-or-later
import unittest

from unittest.mock import patch

import bituldap as b

from tests import config


class SearchTestCase(unittest.TestCase):
    @patch("bituldap.create_connection", return_value=config.connect())
    def test_group_search(self, mock_connect):
        group = b.get_group('www')
        self.assertEqual(group.entry_dn, 'cn=www,ou=groups,dc=example,dc=org')

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_user(self, mock_connect):
        user = b.get_user('eduncan')
        self.assertEqual(user.entry_dn, 'uid=eduncan,ou=people,dc=example,dc=org')
        self.assertEqual(user.loginShell, '/bin/csh')
