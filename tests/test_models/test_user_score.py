# coding: utf-8
"""Tests for the UserScore module."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import django_recommend.models
import quotes.models
from django.contrib.auth import models as auth_models


@pytest.mark.django_db
def test_set_score_with_existing():
    """Trying to set a score that already exists updates the existing row."""
    quote = quotes.models.Quote.objects.create(content='foobar')
    user = auth_models.User.objects.create()
    score = django_recommend.models.UserScore.set(user, quote, 3)

    assert score.pk
    assert score.score == 3

    new_score = django_recommend.models.UserScore.set(user, quote, 7)

    assert new_score.pk == score.pk
    assert new_score.score == 7
