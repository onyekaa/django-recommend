# coding: utf-8
"""Tests for django_recommend.tasks."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect

import mock
import pyrecommend.similarity
import pytest
from django.contrib.contenttypes import models as ct_models

import django_recommend.storage
import django_recommend.tasks
import quotes.models


def get_call_args(mocked_func, mock_call):
    """Get a dictionary of arg values from a mock call.

    Gets *all* args, including defaults specified in the function definition.

    >>> def f(a, b=0, c=1, d=2):
    ...   pass
    >>> f_mock = mock.MagicMock(return_value=None)
    >>> f_mock(3, 4, d=9)
    >>> # What was the value sent to b?
    >>> f_mock.call_args[0][1]
    4
    >>> # What about d?
    >>> f_mock.call_args[1]['d']
    9
    >>> # Not good... lookup method changes depending on if it's given as an
    >>> # arg or a kwarg. Meaning perfectly valid code can break this check.
    >>> get_call_args(f, f_mock.call_args)['b']
    4
    >>> get_call_args(f, f_mock.call_args)['d']
    9
    >>> # That's better
    >>> f_mock('foo', 'bar')
    >>> (get_call_args(f, f_mock.call_args) ==
    ...  {'a': 'foo', 'b': 'bar', 'c': 1, 'd': 2})
    True

    """
    pos_args, key_args = mock_call
    return inspect.getcallargs(mocked_func, *pos_args, **key_args)


@pytest.mark.django_db
def test_calculates_similarity():
    """Calculates similarity using pyrecommend."""
    quote = quotes.models.Quote.objects.create(content='foobar')
    ctype = ct_models.ContentType.objects.get_for_model(quote)
    with mock.patch('pyrecommend.calculate_similarity') as calc_sim:
        django_recommend.tasks.update_similarity((quote.pk, ctype.pk))

    assert calc_sim.called
    args = get_call_args(pyrecommend.calculate_similarity, calc_sim.call_args)
    assert args['dataset'].obj == quote
    assert args['dataset'][quote] == {}  # Getting scores
    assert args['similarity'] == pyrecommend.similarity.dot_product
    assert isinstance(args['result_storage'],
                      django_recommend.storage.ResultStorage)
