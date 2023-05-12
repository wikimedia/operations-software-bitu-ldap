# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import bituldap as b

from unittest.mock import patch

from ldap3 import ServerPool,Server

from tests import config

class UserTestCase(unittest.TestCase):
    def setUp(self):
        config.setup()

    def test_connection_open(self):
        user = b.get_user('millersamantha')
        self.assertEqual(user.uidNumber, 4873)

    @patch('bituldap.__ldap_reconnect', config.connect)
    def test_connection_open(self):
        b.singleton.shared_connection.unbind()
        self.assertTrue(b.singleton.shared_connection.closed)

        user = b.get_user('millersamantha')
        self.assertEqual(user.uidNumber, 4873)