# coding: utf-8
"""Tests for "entry point" functions in django_recommend."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from django.contrib.auth.models import User

import django_recommend.models
import quotes.models


def make_quote(**kwargs):
    """Shorthand for invoking the Quote constructor."""
    return quotes.models.Quote.objects.create(**kwargs)


@pytest.mark.django_db
def test_set_score_request_user(rf):
    """The set_score method associates a score with a user."""

    # Username is irrelevant to the test, but must be unique.
    user = User.objects.create(username='abc', pk=30)
    req = rf.get('/foo')
    req.user = user
    req.session = {}
    quote = make_quote(content='hello world')

    django_recommend.set_score(req, quote, 1)

    assert django_recommend.scores_for(quote) == {'user:30': 1}

    user = User.objects.create(username='xyz', pk=55)
    req = rf.get('/bar')
    req.user = user
    req.session = {}
    quote = make_quote(content='Fizzbuzz')

    django_recommend.set_score(req, quote, 5)

    assert django_recommend.scores_for(quote) == {'user:55': 5}


@pytest.mark.django_db
def test_set_score_direct_user():
    """set_score() can take a user instead of a request."""
    user = User.objects.create(pk=3)
    quote = make_quote(content='fizzbuzz')

    django_recommend.set_score(user, quote, 5)

    assert django_recommend.scores_for(quote) == {'user:3': 5}


@pytest.mark.django_db
def test_get_score_with_user():
    """The get_score function can get the user's score for an object."""
    user = User.objects.create(username='def')
    quote = make_quote(content='fizzbuzz')
    django_recommend.models.UserScore.set(user, quote, 55)

    assert django_recommend.get_score(user, quote) == 55


@pytest.mark.django_db
def test_get_score_when_unset():
    """If a score is not in the DB, 0 is returned."""
    user = User.objects.create()
    quote = make_quote(content='foobar')

    assert django_recommend.models.UserScore.objects.count() == 0
    assert django_recommend.get_score(user, quote) == 0
