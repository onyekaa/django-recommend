# coding: utf-8
"""Test configuration defaults."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from django_recommend import conf


def test_proxies_django_settings(settings):
    """Normal Django settings are accessible through the object."""
    settings.INSTALLED_APPS = ('foo',)
    assert conf.settings.INSTALLED_APPS == ('foo',)

    settings.INSTALLED_APPS = ('bar',)
    assert conf.settings.INSTALLED_APPS == ('bar',)


def test_provides_defaults(settings):
    """Unset app settings get defaults."""
    del settings.RECOMMEND_ENABLE_AUTOCALC

    # Ensure setting is not accessible
    assert not hasattr(settings, 'RECOMMEND_ENABLE_AUTOCALC')
    assert conf.settings.RECOMMEND_ENABLE_AUTOCALC is True


def test_user_overrides(settings):
    """Users can override the defaults."""
    settings.RECOMMEND_ENABLE_AUTOCALC = 'foobar'

    assert conf.settings.RECOMMEND_ENABLE_AUTOCALC == 'foobar'


def test_bogus_setting(settings):
    """Nonexistant settings stil raise AttributeError."""
    with pytest.raises(AttributeError):

        # pylint: disable=pointless-statement
        settings.THIS_ISNT_A_REAL_SETTING
