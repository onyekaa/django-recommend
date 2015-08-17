# coding: utf-8
"""Tests for the template tags."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.template
import mock

import django_recommend
import tests.utils


class FakeObj(object):  # pylint: disable=too-few-public-methods
    """Simple object used for testing templates."""

    def __repr__(self):
        return '{}'.format(id(self))  # unicode() doesn't exist in py3


def test_similar_objects():
    """The similar_objects template filter is a wrapper for the function."""
    mock_obj = object()
    mock_return_value = FakeObj()
    template_src = '{% load django_recommend %}{{ obj|similar_objects }}'
    template = django.template.Template(template_src)
    ctx = django.template.Context({'obj': mock_obj})

    with mock.patch('django_recommend.similar_objects') as similar_objects:
        similar_objects.return_value = (mock_return_value,)
        rendered = template.render(ctx)

    # Square brackets: converts result to list
    assert rendered == '[{}]'.format(mock_return_value)
    args = tests.utils.get_call_args(
        django_recommend.similar_objects, similar_objects.call_args)
    assert args['obj'] is mock_obj
