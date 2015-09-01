# coding: utf-8
"""Settings for the django_recommend app."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.conf


class DefaultSettingsProxy(object):  # pylint: disable=too-few-public-methods
    """A settings proxy that has defaults for this app."""

    RECOMMEND_ENABLE_AUTOCALC = True

    RECOMMEND_PURGE_MISSING_DATA = True

    RECOMMEND_USE_CELERY = True

    def __getattribute__(self, attr_name):
        try:

            # Prefer settings from their Django settings module.
            return getattr(django.conf.settings, attr_name)
        except AttributeError:

            # Nothing found in Django settings, so try to get a default.
            return super(
                DefaultSettingsProxy, self).__getattribute__(attr_name)


settings = DefaultSettingsProxy()  # pylint: disable=invalid-name
