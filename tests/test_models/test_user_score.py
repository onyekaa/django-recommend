# coding: utf-8
"""Tests for the UserScore module."""
# pylint: disable=redefined-outer-name
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
