"""
This module is responsible for setting up the 'client' package using setuptools.
It defines the metadata such as the package name, version, and author, and it
automatically finds all sub-packages that need to be included.

Version: 0.1.0
Author: Cisco Systems, Inc.
"""

from setuptools import setup, find_packages  # type: ignore

setup(
    name="clients",
    version="0.1.0",
    packages=find_packages(include=["tf_ca_clients", "tf_ca_clients.*"])
)
