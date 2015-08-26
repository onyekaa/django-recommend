# coding: utf-8
"""Tests for "entry point" functions in django_recommend."""
# pylint: disable=redefined-outer-name
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mock
import pytest
import testfixtures
from django.contrib.auth.models import User

import django_recommend.models
import people.models
import quotes.models
from tests.utils import make_quote


@pytest.fixture
def some_quote():
    """A throwaway quote for testing."""
    return quotes.models.Quote.objects.create(content='foobar')


@pytest.fixture
def some_other_quote():
    """Another throaway quote for testing."""
    return quotes.models.Quote.objects.create(content='fizzbuzz')


def make_user(**kwargs):
    """Make a user, including password."""
    password = kwargs.pop('password', None)
    user_obj = User.objects.create(**kwargs)
    if password is not None:
        user_obj.set_password(password)
        user_obj.save()
    return user_obj


@pytest.mark.django_db
def test_set_score_request_user(client):
    """The set_score method associates a score with a user."""
    make_user(username='abc', password='foo', pk=30)
    assert client.login(username='abc', password='foo')
    req = client.get('/foo').wsgi_request
    quote = make_quote(content='hello world')

    django_recommend.set_score(req, quote, 1)

    assert django_recommend.scores_for(quote) == {'user:30': 1}

    make_user(username='xyz', password='spongebob3', pk=55)
    assert client.login(username='xyz', password='spongebob3')
    req = client.get('/bar/').wsgi_request
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


@pytest.mark.django_db
def test_setdefault_score():
    """setdefault_score only sets a score if it doesn't exist."""
    user = User.objects.create()
    quote = make_quote(content='foobar')

    assert django_recommend.get_score(user, quote) == 0
    django_recommend.setdefault_score(user, quote, 3)
    assert django_recommend.get_score(user, quote) == 3
    django_recommend.setdefault_score(user, quote, 5)
    assert django_recommend.get_score(user, quote) == 3


@pytest.mark.django_db
def test_setdefault_score_authed(client, some_quote):
    """setdefault_score() takes an authenticated request."""
    user = make_user(username='abc', password='def')
    assert client.login(username='abc', password='def')
    request = client.get('/foobar').wsgi_request

    django_recommend.setdefault_score(request, some_quote, 12)
    assert django_recommend.get_score(user, some_quote) == 12

    # Won't overwrite
    django_recommend.setdefault_score(request, some_quote, 20)
    assert django_recommend.get_score(user, some_quote) == 12


@pytest.mark.django_db
def test_setdefault_score_anon(client, some_quote):
    """setdefault_score() takes an anonymous request."""
    request = client.get('/foobar').wsgi_request
    assert not request.user.is_authenticated()

    django_recommend.setdefault_score(request, some_quote, 9)
    assert django_recommend.get_score(request, some_quote) == 9

    # Won't overwrite
    django_recommend.setdefault_score(request, some_quote, 3)
    assert django_recommend.get_score(request, some_quote) == 9


@pytest.mark.django_db
def test_setdefault_score_str(some_quote):
    """setdefault_score() takes a string."""
    django_recommend.setdefault_score('qwerty', some_quote, 20)
    assert django_recommend.get_score('qwerty', some_quote) == 20

    # Won't overwrite
    django_recommend.setdefault_score('qwerty', some_quote, 3)
    assert django_recommend.get_score('qwerty', some_quote) == 20


@pytest.mark.django_db
def test_get_similar_objects():
    """get_similar_objects gets instances most similar to the given object."""
    quote_a = make_quote('foo')
    quote_b = make_quote('bar')
    quote_c = make_quote('baz')
    django_recommend.models.ObjectSimilarity.set(quote_a, quote_b, 10)
    django_recommend.models.ObjectSimilarity.set(quote_a, quote_c, 5)

    sim_quotes = django_recommend.similar_objects(quote_a)
    assert list(sim_quotes) == [quote_b, quote_c]

    # Change scores to ensure sorted order is given.
    django_recommend.models.ObjectSimilarity.set(quote_a, quote_b, 4)
    django_recommend.models.ObjectSimilarity.set(quote_a, quote_c, 12)

    sim_quotes = django_recommend.similar_objects(quote_a)
    assert list(sim_quotes) == [quote_c, quote_b]

    # Change which object is requested to make sure SUT isn't only filtering
    # against object_1
    sim_quotes = django_recommend.similar_objects(quote_b)
    assert list(sim_quotes) == [quote_a]


@pytest.mark.django_db
def test_similar_objects_multi_db():
    """get_similar_objects doesn't crash when models are in different DBs."""
    pam = people.models.Person.objects.create(name='Pam')
    jim = people.models.Person.objects.create(name='Jim')
    toby = people.models.Person.objects.create(name='Toby')
    django_recommend.models.ObjectSimilarity.set(pam, jim, 10)
    django_recommend.models.ObjectSimilarity.set(pam, toby, 11)
    django_recommend.models.ObjectSimilarity.set(jim, toby, 2)

    sim_people = django_recommend.similar_objects(pam)

    assert list(sim_people) == [toby, jim]


@pytest.mark.django_db
def test_set_score_anon_request(client, some_quote, some_other_quote):
    """set_score() accepts a request."""
    resp = client.get('/foo')  # Don't care about response
    req = resp.wsgi_request
    assert not req.user.is_authenticated()
    assert req.session.session_key

    django_recommend.set_score(req, some_quote, 343)
    assert django_recommend.get_score(req, some_quote) == 343

    django_recommend.set_score(req, some_other_quote, 242)
    assert django_recommend.get_score(req, some_other_quote) == 242


@pytest.mark.django_db
def test_similar_to():
    """similar_to is like similar_objects but returns a queryset."""
    quote_a = make_quote('foo')
    quote_b = make_quote('bar')
    quote_c = make_quote('baz')
    sim_ab = django_recommend.models.ObjectSimilarity.set(quote_a, quote_b, 10)
    sim_ac = django_recommend.models.ObjectSimilarity.set(quote_a, quote_c, 5)

    sim_quotes = django_recommend.similar_to(quote_a)
    assert list(sim_quotes) == [sim_ab, sim_ac]

    sim_quotes = sim_quotes.exclude_objects(
        quotes.models.Quote.objects.filter(pk=quote_b.pk))
    assert list(sim_quotes) == [sim_ac]


@pytest.mark.django_db
def test_set_score_blank_session(client):
    """set_score() just logs a warning with a blank session."""
    bogus = object()  # Object shouldn't matter/need to be a Django model
    request = client.get('/url-doesnt-matter').wsgi_request
    blank_session = mock.patch.object(type(request.session), 'session_key', '')

    with testfixtures.LogCapture() as logs, blank_session:
        django_recommend.set_score(request, bogus, 3)

    # By this point it is clear no database saving happened, because
    # attempting to associate anything with non-orm bogus object will crash.

    msg = ("Can't track score: anonymous user has no session key. Do you need "
           'to set SESSION_SAVE_EVERY_REQUEST=True ?')
    logs.check(('django_recommend', 'WARNING', msg))
