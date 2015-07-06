#!/usr/bin/env python
"""
Freight
=======

A deploy service.

:copyright: (c) 2015 GetSentry LLC
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

tests_require = [
    'flake8>=2.1.0,<2.2.0',
    'mock>=1.0.1,<1.1.0',
    'loremipsum>=1.0.5,<1.1.0',
    'pytest>=2.5.0,<2.6.0',
    'pytest-cov>=1.6,<1.7',
    'pytest-timeout>=0.3,<0.4',
    'pytest-xdist>=1.9,<1.10',
    'responses>=0.3.0,<0.4.0',
]


install_requires = [
    'alembic>=0.7.4,<0.8.0',
    'blessings>=1.6.0,<1.7.0',
    'blinker>=1.3.0,<1.4.0',
    'celery>=3.1.18,<3.2.0',
    'flask>=0.10.1,<0.11.0',
    'flask-heroku>=0.1.9,<0.2.0',
    'flask-sslify>=0.1.4,<0.2.0',
    'flask-sqlalchemy>=1.0,<1.1',
    'flask-redis>=0.0.6,<0.1.0',
    'flask-restful>=0.3.1,<0.4.0',
    'oauth2client>=1.2,<1.3',
    'psycopg2>=2.5.1,<2.6.0',
    'raven>=5.1.1,<5.2.0',
    'redis>=2.10.3,<2.11.0',
    'requests>=2.5.1,<2.6.0',
    'uwsgi>=2.0.9,<2.1.0',
]

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
