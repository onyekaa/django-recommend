# coding: utf-8
"""Tests for the data access bridge."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.db.models
import pytest
from django.contrib.contenttypes import models as ct_models

import django_recommend.storage
import django_recommend.tasks
import quotes.models
import people.models
from tests.utils import make_quote


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


@pytest.mark.django_db
def test_missing_nopurge(settings):
    """Raises exceptions when purge is not set."""
    quote = sample_data()
    quote[2].delete()
    settings.RECOMMEND_PURGE_MISSING_DATA = False

    obj_data = django_recommend.storage.ObjectData(quote[1])

    with pytest.raises(quotes.models.Quote.DoesNotExist):
        obj_data.keys()


@pytest.mark.django_db
def test_missing_purge(settings):
    """Deletes similarity data when purge is set."""
    Q = django.db.models.Q  # pylint: disable=invalid-name
    quote = sample_data()
    ctype = ct_models.ContentType.objects.get_for_model(quote[2])
    django_recommend.tasks.update_similarity((quote[1].pk, ctype.pk))
    quote_2_id = quote[2].pk
    quote[2].delete()
    assert 2 == django_recommend.models.UserScore.objects.filter(
        object_content_type=ctype, object_id=quote_2_id).count()
    assert 1 == django_recommend.models.ObjectSimilarity.objects.filter(
        Q(object_1_content_type=ctype, object_1_id=quote_2_id) |
        Q(object_2_content_type=ctype, object_2_id=quote_2_id)).count()
    settings.RECOMMEND_PURGE_MISSING_DATA = True

    obj_data = django_recommend.storage.ObjectData(quote[1])
    keys = obj_data.keys()

    assert [quote[1]] == keys
    assert 0 == django_recommend.models.UserScore.objects.filter(
        object_content_type=ctype, object_id=quote_2_id).count()
    assert 0 == django_recommend.models.ObjectSimilarity.objects.filter(
        Q(object_1_content_type=ctype, object_1_id=quote_2_id) |
        Q(object_2_content_type=ctype, object_2_id=quote_2_id)).count()
