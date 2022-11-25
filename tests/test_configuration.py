# SPDX-License-Identifier: GPL-3.0-or-later
import json
import tempfile
import unittest

from pathlib import Path

import bituldap as b


class ConfigurationFileTestCase(unittest.TestCase):
    config_file = Path.joinpath(Path(tempfile.gettempdir()), 'test_ldap_conf.json')

    def setUp(self):
        self.config = {
            'uri': 'ldap://localhost:1389',
            'username': 'cn=admin,dc=example,dc=org',
            'password': 'adminpassword',
            'read_only': 'False',
            'users': {
                'dn': 'ou=people,dc=example,dc=org',
                'object_classes': ['inetOrgPerson', 'posixAccount']
            }
        }

        with open(self.config_file, "w") as outfile:
            json.dump(self.config, outfile)

    def test_config_file_parser(self):
        success, c = b.configure.file(Path(self.config_file))
        self.assertFalse(c.read_only)
        self.assertEqual(c.users.object_classes, ['inetOrgPerson', 'posixAccount'])
        self.assertEqual(c.groups.dn, 'ou=groups,dc=example,dc=org')
        self.assertEqual(c.servers[0].port, 1389)

    def test_multi_server(self):
        self.config['uri'] = ['ldap://localhost:1389', 'ldaps://localhost:1636',]
        with open(self.config_file, "w") as outfile:
            json.dump(self.config, outfile)

        success, c = b.configure.file(Path(self.config_file))
        self.assertEqual(len(c.servers), 2)
        ports = [server.port for server in c.servers]
        self.assertEqual(ports, [1389, 1636])