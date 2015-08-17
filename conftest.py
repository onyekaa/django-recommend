# coding: utf-8
"""Settings for py.test command."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from django.conf import settings

import os.path
import sys


REPO_ROOT = os.path.realpath(os.path.dirname(__file__))
TESTPROJ_ROOT = os.path.join(REPO_ROOT, 'simplerec')


def pytest_configure():
    """Add a small Django config to enable DB use in tests."""
    sys.path.append(TESTPROJ_ROOT)
    settings.configure(
        RECOMMEND_ENABLE_AUTOCALC=False,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'},
                   'second': {'ENGINE': 'django.db.backends.sqlite3'}},
        MIDDLEWARE_CLASSES=(),
        DATABASE_ROUTERS=['people.routers.DatabaseRouter'],
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',

            'django_recommend',

            'people',
            'quotes',
        ))
