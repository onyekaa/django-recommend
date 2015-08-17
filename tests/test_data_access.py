# coding: utf-8
"""Tests for the data access bridge."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import django_recommend.storage
import people.models
import quotes.models


def make_quote(content, **kwargs):
    """A shorthand for the Quote constructor."""
    kwargs['content'] = content
    return quotes.models.Quote.objects.create(**kwargs)


def sample_data():
    """Create a set of sample data."""
    quote = {
        1: make_quote('quote 1'),
        2: make_quote('quote 2'),
        3: make_quote('quote 3'),
        4: make_quote('quote 4'),
    }

    django_recommend.set_score('foo', quote[1], 3)
    django_recommend.set_score('foo', quote[2], 2)
    django_recommend.set_score('bar', quote[2], 3)
    django_recommend.set_score('bar', quote[3], 4)
    django_recommend.set_score('baz', quote[4], 5)

    # Note: quote 4/baz are not related to other users/quotes.

    return quote


@pytest.mark.django_db
def test_gets_related_items():
    """All items by all relevant users are retrieved."""
    quote = sample_data()

    obj_data = django_recommend.storage.ObjectData(quote[1])
    assert set(obj_data.keys()) == {quote[1], quote[2]}

    obj_data = django_recommend.storage.ObjectData(quote[2])
    assert set(obj_data.keys()) == {quote[1], quote[2], quote[3]}

    obj_data = django_recommend.storage.ObjectData(quote[3])
    assert set(obj_data.keys()) == {quote[2], quote[3]}

    obj_data = django_recommend.storage.ObjectData(quote[4])
    assert set(obj_data.keys()) == {quote[4]}


@pytest.mark.django_db
def test_gets_scores_for_one_item():
    """Accessing a specific item gets all the scores for it."""
    quote = sample_data()

    obj_data = django_recommend.storage.ObjectData(quote[2])
    assert obj_data[quote[2]] == {'foo': 2, 'bar': 3}

    obj_data = django_recommend.storage.ObjectData(quote[4])
    assert obj_data[quote[4]] == {'baz': 5}


@pytest.mark.django_db
def test_data_multiple_dbs():
    """Can retrieve objects from other databases."""
    ryan = people.models.Person.objects.create(name='Ryan')
    toby = people.models.Person.objects.create(name='Toby')
    django_recommend.set_score('michael', ryan, 20)
    django_recommend.set_score('michael', toby, 1)

    data = django_recommend.storage.ObjectData(ryan)

    assert set(data) == {ryan, toby}
