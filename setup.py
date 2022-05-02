#!/usr/bin/env python
"""
Freight
=======

A deploy service.

:copyright: (c) 2015 Functional Software Inc.
:license: Apache 2.0, see LICENSE for more details.
"""


from setuptools import setup, find_packages


with open("requirements-pre-commit.txt") as file:
    pre_commit_requires = file.read().splitlines()

with open("requirements-test.txt") as file:
    tests_require = file.read().splitlines()

with open("requirements.txt") as file:
    install_requires = file.read().splitlines()

setup(
    name="freight",
    version="0.0.0",
    author="David Cramer",
    author_email="dcramer@gmail.com",
    url="https://github.com/getsentry/freight",
    description="A deployment service",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        "test": tests_require,
        "pre-commit": pre_commit_requires,
    },
    license="Apache 2.0",
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
)
