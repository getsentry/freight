from __future__ import absolute_import

import os
import subprocess

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('freight').version
except Exception:
    VERSION = 'unknown'


def _get_git_revision(path):
    try:
        r = subprocess.check_output('git rev-parse HEAD', cwd=path, shell=True)
    except Exception:
        return None
    return r.strip()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir))
    path = os.path.join(checkout_dir, '.git')
    if os.path.exists(path):
        return _get_git_revision(path)
    return None


def get_version():
    base = VERSION
    if __build__:
        base = '%s (%s)' % (base, __build__)
    return base


__build__ = get_revision()
__docformat__ = 'restructuredtext en'
