# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass
from typing import Union


@dataclass
class LdapQueryOptions:
    """Data class for storing information on LDAP object type.
    Location, primary object classes and auxiliary object classes.
    """
    dn: str
    object_classes: Union[str, list[str]]
    auxiliary_classes: Union[str, list[str]]


@dataclass
class Configuration:
    """Data class for storing LDAP connection information and information
    regarding the structure of the LDAP data.
    """
    host: str
    port: int
    username: str
    password: str
    read_only: bool
    tls: bool
    users: LdapQueryOptions
    groups: LdapQueryOptions
