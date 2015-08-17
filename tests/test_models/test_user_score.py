# coding: utf-8
"""Tests for the UserScore module."""
# pylint: disable=redefined-outer-name
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mock
import pytest

import django_recommend.models
import quotes.models
from django.contrib.auth import models as auth_models


@pytest.fixture
def test_quote():
    """A test quote instance."""
    return quotes.models.Quote.objects.create(content='foobar')


@pytest.mark.django_db
def test_set_score_with_existing(test_quote):
    """Trying to set a score that already exists updates the existing row."""
    user = auth_models.User.objects.create()
    score = django_recommend.models.UserScore.set(user, test_quote, 3)

    assert score.pk
    assert score.score == 3

    new_score = django_recommend.models.UserScore.set(user, test_quote, 7)

    assert new_score.pk == score.pk
    assert new_score.score == 7


@pytest.mark.django_db
def test_set_score_with_str(test_quote):
    """set_score() can take a str instead of a User instance."""
    assert django_recommend.models.UserScore.get('foo', test_quote) == 0

    django_recommend.models.UserScore.set('foo', test_quote, 3)
    assert django_recommend.models.UserScore.get('foo', test_quote) == 3


@pytest.mark.django_db
def test_signal_handler(test_quote):
    """A new score object triggers the execution of the signal handler."""
    with mock.patch('django_recommend.tasks.signal_handler') as sig_handler:
        score_obj = django_recommend.set_score('foo', test_quote, 4)
    assert sig_handler.called
    assert sig_handler.call_args[1]['instance'] == score_obj

    # Only listens to signals from UserScore
    with mock.patch('django_recommend.tasks.signal_handler') as sig_handler:
        quotes.models.Quote.objects.create(content='fizzbuzz')

    assert not sig_handler.called


@pytest.mark.django_db
def test_signal_handler_delete(test_quote):
    """Deleting a score object triggers execution of the signal handler."""
    score_obj = django_recommend.set_score('foo', test_quote, 3)

    with mock.patch('django_recommend.tasks.signal_handler') as sig_handler:
        score_obj.delete()

    assert sig_handler.called
    assert sig_handler.call_args[1]['instance'] == score_obj

    # Ensure it's only for UserScore objects.
    with mock.patch('django_recommend.tasks.signal_handler') as sig_handler:
        test_quote.delete()

    assert not sig_handler.called
