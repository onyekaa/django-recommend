# coding: utf-8
"""Tests for django_recommend.tasks."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mock
import pyrecommend.similarity
import pytest
from django.contrib.contenttypes import models as ct_models

import django_recommend.storage
import django_recommend.tasks
import quotes.models
import tests.utils


@pytest.mark.django_db
def test_calculates_similarity():
    """Calculates similarity using pyrecommend."""
    quote = quotes.models.Quote.objects.create(content='foobar')
    ctype = ct_models.ContentType.objects.get_for_model(quote)
    with mock.patch('pyrecommend.calculate_similarity') as calc_sim:
        django_recommend.tasks.update_similarity((quote.pk, ctype.pk))

    assert calc_sim.called
    args = tests.utils.get_call_args(
        pyrecommend.calculate_similarity, calc_sim.call_args)
    assert args['dataset'].obj == quote
    assert args['dataset'][quote] == {}  # Getting scores
    assert args['similarity'] == pyrecommend.similarity.dot_product
    assert isinstance(args['result_storage'],
                      django_recommend.storage.ResultStorage)


@pytest.mark.django_db
def test_autocalc(settings):
    """The signal handler will update similarity when AUTOCALC is enabled."""
    settings.RECOMMEND_ENABLE_AUTOCALC = True
    django_recommend.tasks.ENABLE_BREAKPOINT = True
    quote = quotes.models.Quote.objects.create(content='foobar')
    quote_ctype = ct_models.ContentType.objects.get_for_model(quote)

    with mock.patch('django_recommend.tasks.update_similarity') as update_sim:
        django_recommend.set_score('foo', quote, 3)

    assert update_sim.delay.called
    args = tests.utils.get_call_args(
        django_recommend.tasks.update_similarity, update_sim.delay.call_args)
    assert args['obj_params'] == (quote.pk, quote_ctype.pk)
