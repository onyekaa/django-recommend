# coding: utf-8
"""Test configuration defaults."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def test_proxies_django_settings():
    """Normal Django settings are accessible through the object."""
    import pytest
    pytest.skip("Don't remember how to override django settings during test.")
