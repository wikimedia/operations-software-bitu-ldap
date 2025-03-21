# SPDX-License-Identifier: GPL-3.0-or-later
from typing import List, Tuple, Union

from ldap3.core.exceptions import LDAPSessionTerminatedByServerError
from ldap3.utils.conv import escape_filter_chars
from ldap3.utils.hashed import hashed
from ldap3 import (FIRST, HASHED_SALTED_SHA, MODIFY_REPLACE,
                   Connection, Entry, ObjectDef, Reader,
                   ServerPool, Writer)

from . import configure, singleton
from .types import Configuration, LdapQueryOptions


def read_configuration() -> Configuration:
    """Read configuration and set singleton.

    Returns:
        Configuration (Configuration): Configuration data class.
    """
    if singleton.shared_configuration is None:
        # Attempt to configure using Django.
        success, configuration = configure.django()
        if success and isinstance(configuration, Configuration):
            singleton.shared_configuration = configuration
            return singleton.shared_configuration

        # Attempt file configuration.
        success, configuration = configure.file()
        if success and isinstance(configuration, Configuration):
            singleton.shared_configuration = configuration
            return singleton.shared_configuration

        # Load configuration from environment variables.
        configuration = configure.environment()
        singleton.shared_configuration = configuration
    return singleton.shared_configuration


def __ldap_reconnect() -> Tuple[bool, Connection]:
    """Create a new connection to an LDAP server

    This function exists separate from the create_connection()
    to facilitate easier unittesting, by allowing the LDAP
    connection to be mocked, while retaining reconnect logic.

    Returns:
        bool: Successfully connected to LDAP server.
        Connection: LDAP connection object.
    """
    config = read_configuration()
    server_pool = ServerPool(config.servers, FIRST)
    connection = Connection(server=server_pool,
                            user=config.username,
                            password=config.password,
                            read_only=config.read_only)
    bound = connection.bind()
    return bound, connection


def create_connection() -> Tuple[bool, Connection]:
    """Creates a new connection to an LDAP server.

    Returns:
        bool: Successfully connected to LDAP server.
        Connection: LDAP connection object.
    """
    return __ldap_reconnect()


def ldap_query(connection: Connection,
               object_def: ObjectDef,
               dn: str, query: str) -> Union[Reader, Writer]:
    """Query LDAP server and reader or writer object. The reader cursor is
    converted to a writer, if the connection to LDAP is defined as read/write.
    If not, a reader is returned

    Args:
        connection (Connection): LDAP connection
        object_def (ObjectDef): Object representation of the LDAP object
            classes
            (https://ldap3.readthedocs.io/en/latest/abstraction.html#objectdef-class).
        dn (str): Distinguished Name of the LDAP subtree that is to be queried.
        query (str): LDAP query, in either standard LDAP query language, or
            LDAP3 Simplified Query Language
            (https://ldap3.readthedocs.io/en/latest/abstraction.html#simplified-query-language)

    Returns:
        Union[Reader, Writer]: LDAP server response, as a reader or writer
            object. The only functional difference between the two types
            are the ability to commit changes to the LDAP server.
    """

    reader = Reader(connection, object_def, dn, escape_filter_chars(query))

    try:
        reader.search()
    except LDAPSessionTerminatedByServerError:
        bound, c = create_connection()
        return ldap_query(c, object_def, dn, query)

    if not connection.read_only:
        writer = Writer.from_cursor(reader)
        return writer
    return reader


def new_entry(options: LdapQueryOptions, dn: str) -> Entry:
    """_summary_

    Args:
        options (LdapQueryOptions): Settings objects containing object
            classes of the LDAP object to create
        dn (str): Distinguished Name of the new object.

    Returns:
        Entry: Newly created, but not committed LDAP object.
            Actual attributes will depend on the specified object
            classes.
    """
    bound, connection = create_connection()
    if not bound:
        return Entry(dn=dn, cursor=None)
    object_def = ObjectDef(options.object_classes,
                           connection,
                           auxiliary_class=options.auxiliary_classes)
    writer = Writer(connection, object_def)
    return writer.new(dn)


def get_single_object(query_options: LdapQueryOptions,
                      attr: str,
                      value: str) -> Union[None, Entry]:
    """Fetch a single object from LDAP.

    Args:
        query_options (LdapQueryOptions): Settings object containing
            object classes and base dn for the queried object.
        attr (str): LDAP attribute to query on.
        value (str): Value of the LDAP attribute queried.

    Raises:
        Exception: The result yielded more entries than expected.

    Returns:
        Union[None, Entry]: Return either the LDAP object if found, or None.
    """
    bound, connection = create_connection()
    if not bound:
        return None

    object_def = ObjectDef(query_options.object_classes,
                           connection,
                           auxiliary_class=query_options.auxiliary_classes)

    # Also get modification timestamp for the requested object.
    object_def += ['modifyTimestamp']
    result = ldap_query(connection, object_def,
                        query_options.dn, f'{attr}: {value}')
    if len(result) == 0:
        return None
    elif len(result) > 1:
        raise Exception("Result set larger than expected")
    return result[0]


def next_uid_number() -> int:
    """Find the next unused POSIX user ID. This will always
    be zero, if no posixAccount objects exists.

    Returns:
        int: POSIX user ID.
    """
    config = read_configuration()
    bound, connection = create_connection()

    # Query does not need to be configurable, beyond dn,
    # as uidNumber is only provided by the posixAccount
    # schema.
    results = connection.extend.standard.paged_search(
        config.users.dn,
        '(objectClass=posixAccount)',
        attributes=['uidNumber'],
        paged_size=1000,
        generator=True
        )
    uids = [result['attributes']['uidNumber'] for result in results]
    return max(uids) + 1


def next_gid_number() -> int:
    """Find the next used POSIX group ID. Will always return zero
    if no posixGroups are found.

    Returns:
        int: POSIX group ID
    """

    # Get all groups using the posixGroup object class, filtering out
    # any "groups" without a gidNumber.
    groups = list_groups("objectClass: posixGroup")
    if len(groups) == 0:
        return 0
    gid_numbers = [group.gidNumber.value for group in groups]
    return max(gid_numbers) + 1


def new_user(uid: str) -> Entry:
    """Create a new user object in LDAP. The user will be created
    in the subtree specified in the configuration. If the method
    "entry_commit_changes()" is not called on the returning object,
    the entry will be discarded once the program ends.

    Args:
        uid (str): Account name for the new user.

    Returns:
        Entry: Create, but not committed user entry.
    """
    config = read_configuration()
    dn = f'uid={uid},{config.users.dn}'
    user = new_entry(config.users, dn)
    return user


def new_group(cn: str, gid_number: int = 0,
              members: list[str] = [],
              description: str = '') -> Tuple[bool, Entry]:
    """Create a new group object in LDAP. The group will be created
    in the subtree specified in the configuration. If the method
    "entry_commit_changes()" is not called on the returning object,
    the entry will be discarded once the program ends.

    Args:
        cn (str): Name of the group to create.

    Returns:
        bool: Group created successfully.
        Entry: Create, but not committed group entry.
    """
    config = read_configuration()
    dn = f'cn={cn},{config.groups.dn}'
    group = new_entry(config.groups, dn)
    group.member = members

    if not members:
        return False, group

    if gid_number == 0:
        group.gidNumber = next_gid_number()
    else:
        group.gidNumber = gid_number

    if description:
        group.description = description

    created: bool = group.entry_commit_changes()
    return created, group


def get_user(uid: str) -> Union[None, Entry]:
    """Fetch a single LDAP user object based on username.

    Args:
        uid (str): Username

    Returns:
        Union[None, Entry]: LDAP entry, or None if user does not exists.
    """
    config = read_configuration()
    return get_single_object(config.users, 'uid', uid)


def get_group(cn: str) -> Union[None, Entry]:
    """Fetch a single LDAP group object, based on group name.

    Args:
        cn (str): Common Name of group

    Returns:
        Union[None, Entry]: LDAP entry, or None if group does not exists.
    """
    config = read_configuration()
    return get_single_object(config.groups, 'CommonName', cn)


def list_groups(query='CommonName: *') -> List[Entry]:
    """List available groups in LDAP

    Args:
        query (str, optional): Optional filter to apply. Defaults
            to "CommonName: \\*" for all group objects.
        attributes: LDAP attributes to return in reader.
                    Default is to exclude members.

    Returns:
        List[Entry]: List of groups.
    """
    bound, connection = create_connection()
    if not bound:
        return []

    config = read_configuration()
    group = ObjectDef(config.groups.object_classes,
                      connection,
                      auxiliary_class=config.groups.auxiliary_classes)

    reader = Reader(connection,
                    group,
                    config.groups.dn,
                    query)

    reader.search()
    return [group for group in reader]


def member_of(dn: str) -> List[Entry]:
    """Query LDAP for group membership

    Args:
        dn (str): Distinguished Name of a group member/user

    Returns:
        List[Entry]: List of groups.
    """
    query = f"(&(objectClass=groupOfNames)(member={dn}))"
    return list_groups(query)


def set_user_password(dn: str, password: str) -> bool:
    """Set a password for a given user DN.

    Args:
        dn (str): Distinguished Name of the user.
        password (str): New password

    Returns:
        bool: Password updated successfully, True or False.
    """
    success, connection = create_connection()
    if not success:
        return success

    hashed_password = hashed(HASHED_SALTED_SHA, password)
    return connection.modify(dn, {'userPassword': [
                                  (MODIFY_REPLACE, [hashed_password])]})
