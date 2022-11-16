# SPDX-License-Identifier: GPL-3.0-or-later
import json
from os import environ
from pathlib import Path
from typing import Union, Tuple

from ldap3.utils.uri import parse_uri  # type: ignore

from .types import Configuration, LdapQueryOptions


def list_from_environ(key: str, default: list[str]) -> list[str]:
    """Parse values from environment variables and ensure that comma-separated
    values are converted to lists.

    Args:
        key (str): Environment variable name
        default (list[str]): Default value if environment variable is not set.

    Returns:
        list[str]: list of variable values.
    """
    value = environ.get(key, "")
    if value:
        return value.split(",")
    return default


def parse_dict(data: dict) -> Configuration:
    """Convert a dict to a Configuration object. The dict is provided by
    either django or a configuration file

    Args:
        data (dict): Data in dictionary form

    Returns:
        Configuration: Configuration object created from dict data.
    """
    users_cfg = data.get("users", {})
    group_cfg = data.get("groups", {})
    uri = parse_uri(data.get("uri", "ldap://localhost"))

    users = LdapQueryOptions(
        dn=users_cfg.get("dn", "ou=users,dc=example,dc=org"),
        object_classes=users_cfg.get("object_classes", ["inetOrgPerson"]),
        auxiliary_classes=users_cfg.get("auxiliary_classes", []),
    )

    groups = LdapQueryOptions(
        dn=group_cfg.get("dn", "ou=groups,dc=example,dc=org"),
        object_classes=group_cfg.get("object_classes", ["groupOfNames"]),
        auxiliary_classes=group_cfg.get("auxiliary_classes", []),
    )

    return Configuration(
        host=uri["host"],
        port=uri["port"],
        username=data.get("username", "cn=admin,dc=example,dc=org"),
        password=data.get("password", ""),
        read_only=data.get("readonly", False),
        tls=uri["ssl"],
        users=users,
        groups=groups,
    )


def django() -> Tuple[bool, Union[Configuration, None]]:
    """Attempt to load configuration from a Django settings file.

    Returns:
        Union[Configuration, bool]: Configuration object, if the project is
        a django project, and settings have the correct configuration data.
        Else return False.
    """
    try:
        from django.conf import settings  # type: ignore
        return True, parse_dict(settings.BITU_LDAP)
    except ModuleNotFoundError:
        # Probably not a Django project then.
        pass
    except Exception:
        # This is a Django project, but the settings does
        # not have the required values.
        pass
    return False, None


def environment() -> Configuration:
    """Read library configuration from enviroment variables.
    This is serving as our default, and will always result in a Configuration
    object.

    Returns:
        Configuration: Configuration object.
    """
    users = LdapQueryOptions(
        dn=environ.get("BITU_USER_DN", "ou=users,dc=example,dc=org"),
        object_classes=list_from_environ("BITU_USER_CLASSES",
                                         ["inetOrgPerson"]),
        auxiliary_classes=list_from_environ("BITU_USER_AUX", []),
    )

    groups = LdapQueryOptions(
        dn=environ.get("BITU_GROUP_DN", "ou=groups,dc=example,dc=org"),
        object_classes=list_from_environ("BITU_GROUP_CLASSES",
                                         ["groupOfNames"]),
        auxiliary_classes=list_from_environ("BITU_GROUP_AUX", []),
    )

    uri = parse_uri(environ.get("BITU_LDAP_URI", "ldap://localhost"))
    read_only = environ.get("BITU_LDAP_READONLY", True)
    if isinstance(read_only, str) and read_only.lower() == "false":
        read_only = False

    configuration = Configuration(
        host=uri["host"],
        port=uri["port"],
        username=environ.get("BITU_USERNAME", "cn=admin,dc=example,dc=org"),
        password=environ.get("BITU_PASSWORD", ""),
        read_only=bool(read_only),
        tls=uri["ssl"],
        users=users,
        groups=groups,
    )

    return configuration


def file(path: Path) -> Configuration:
    """Read configuration from a file, JSON formatted.

    Args:
        path (Path): Path to configuration

    Returns:
        Configuration: Configuration object.
    """
    with open(path, mode="r") as fp:
        data = json.load(fp)
        return parse_dict(data)
