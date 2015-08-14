# coding: utf-8
"""Test configuration defaults."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django_recommend import conf


def test_proxies_django_settings(settings):
    """Normal Django settings are accessible through the object."""
    settings.INSTALLED_APPS = ('foo',)
    assert conf.settings.INSTALLED_APPS == ('foo',)

    settings.INSTALLED_APPS = ('bar',)
    assert conf.settings.INSTALLED_APPS == ('bar',)
