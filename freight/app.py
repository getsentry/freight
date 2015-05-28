"""
This file acts as a default entry point for app creation.
"""
from __future__ import absolute_import

from freight.config import create_app, celery  # NOQA

app = create_app()
