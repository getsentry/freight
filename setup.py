#!/usr/bin/env python
"""
Freight
=======

A deploy service.

:copyright: (c) 2015 Functional Software Inc.
:license: Apache 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import

import os.path

from setuptools import setup, find_packages


# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

with open('requirements-test.txt') as file:
    tests_require = file.read().splitlines()

with open('requirements.txt') as file:
    install_requires = file.read().splitlines()

setup(
    name='freight',
    version='0.0.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='https://github.com/getsentry/freight',
    description='A deployment service',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': tests_require,
    },
    license='Apache 2.0',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
