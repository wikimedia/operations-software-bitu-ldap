# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
import bituldap as b

from unittest.mock import patch

from tests import config

class UserTestCase(unittest.TestCase):

    @patch("bituldap.create_connection", return_value=config.connect())
    def test_connection_open(self, mock_connect):
        user = b.get_user('millersamantha')
        self.assertEqual(user.uidNumber, 4873)
