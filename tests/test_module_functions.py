# coding: utf-8
"""Tests for "entry point" functions in django_recommend."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from django.contrib.auth.models import User

import django_recommend.models
import quotes.models


@pytest.mark.django_db
def test_set_score_with_user(rf):
    """The set_score method associates a score with a user."""

    # Username is irrelevant to the test, but must be unique.
    user = User.objects.create(username='abc', pk=30)
    req = rf.get('/foo')
    req.user = user
    req.session = {}
    quote = quotes.models.Quote.objects.create(content='hello world')

    django_recommend.set_score(req, quote, 1)

    assert django_recommend.scores_for(quote) == {'user:30': 1}

    user = User.objects.create(username='xyz', pk=55)
    req = rf.get('/bar')
    req.user = user
    req.session = {}
    quote = quotes.models.Quote.objects.create(content='Fizzbuzz')

    django_recommend.set_score(req, quote, 5)

    assert django_recommend.scores_for(quote) == {'user:55': 5}


@pytest.mark.django_db
def test_get_score_with_user():
    """The get_score function can get the user's score for an object."""
    user = User.objects.create(username='def')
    quote = quotes.models.Quote.objects.create(content='fizzbuzz')
    django_recommend.models.UserScore.set(user, quote, 55)

    assert django_recommend.get_score(user, quote) == 55
