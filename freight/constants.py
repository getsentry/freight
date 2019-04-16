import os
import sys


def get_python_version():
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"


PYTHON_VERSION = get_python_version()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
