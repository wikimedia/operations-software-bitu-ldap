# SPDX-License-Identifier: GPL-3.0-or-later
from setuptools import find_packages, setup

setup(
   name='Bitu LDAP',
   version='0.0.1',
   description='Object oriented wrapper for interacting with LDAP users and groups',
   author='Simon Lyngshede',
   author_email='slyngshede@wikimedia.org',
   url='https://gerrit.wikimedia.org/r/admin/repos/operations/software/bitu-ldap',
   packages=find_packages(exclude=["*.tests", "*.tests.*"]),
   install_requires=['ldap3'], #external packages as dependencies
   package_data={"bituldap": ["py.typed"]},
)
