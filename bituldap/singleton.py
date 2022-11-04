# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Optional
from ldap3 import Connection  # type: ignore

from .types import Configuration


""" The singleton module holds shared connection and configuration objects.
    These are not intended to be accessed directly, but only via the functions:
    create_connection and read_configuration in the __init__.py.

    Using the function to access the variables will ensure correct
    initialization.

    This module exploits the fact that variables in modules are always
    singletons by default.

    Variables:
        shared_connection (Connection): Connection singleton.
        shared_configuration (Configuration): Configuration singleton.
"""

shared_connection: Optional[Connection] = None
shared_configuration: Optional[Configuration] = None
