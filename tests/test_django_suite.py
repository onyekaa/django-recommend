# coding: utf-8
"""Run the Django app tests."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def test_passes_check():
    """django_recommend passes `manage.py check`"""
    from django.core.management import call_command

    call_command('check', 'django_recommend')
