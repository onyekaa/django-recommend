# coding: utf-8
"""Tests for ObjectSimilarity."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mock
import pytest
from django.contrib.contenttypes import models as ct_models

import quotes.models
from django_recommend import models
from tests.utils import make_quote


@pytest.mark.django_db
def test_set_bad_order():
    """ObjectSimilarity.set() always stores in the same order."""
    quote_a = make_quote(content='Hello', pk=30)
    quote_b = make_quote(content='World', pk=40)

    sim_obj = models.ObjectSimilarity.set(quote_a, quote_b, 10)

    assert sim_obj.object_1 == quote_a
    assert sim_obj.object_2 == quote_b

    # Give quotes in other order and make sure the same result happens.
    sim_obj.delete()
    sim_obj = models.ObjectSimilarity.set(quote_b, quote_a, 20)

    assert sim_obj.object_1 == quote_a
    assert sim_obj.object_2 == quote_b


@pytest.mark.django_db
def test_set_existing():
    """Setting a similarity for an existing pair just updates the score."""
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')

    sim_obj = models.ObjectSimilarity.set(obj_a, obj_b, 10)
    sim_obj_2 = models.ObjectSimilarity.set(obj_a, obj_b, 20)

    assert sim_obj.pk == sim_obj_2.pk
    assert sim_obj_2.score == 20


@pytest.mark.django_db
def test_set_existing_to_0():
    """A score of 0 causes deletion of an existing ObjectSimilarity."""
    obj_a = make_quote('Hello', pk=12)
    obj_b = make_quote('World', pk=22)
    sim_obj = models.ObjectSimilarity.set(obj_a, obj_b, 10)
    ctype = ct_models.ContentType.objects.get_for_model(obj_a)

    models.ObjectSimilarity.set(obj_a, obj_b, 0)

    with pytest.raises(models.ObjectSimilarity.DoesNotExist):
        models.ObjectSimilarity.objects.get(pk=sim_obj.pk)

    assert not models.ObjectSimilarity.objects.filter(
        object_1_content_type=ctype, object_2_content_type=ctype,
        object_1_id=obj_a.id, object_2_id=obj_b.pk).exists()


@pytest.mark.django_db
def test_set_0_doesnt_create():
    """Giving a pair of new objects a score of 0 does nothing."""
    obj_a = make_quote('Hello', pk=12)
    obj_b = make_quote('World', pk=22)
    ctype = ct_models.ContentType.objects.get_for_model(obj_a)

    sim_obj = models.ObjectSimilarity.set(obj_a, obj_b, 0)

    assert sim_obj is None
    assert not models.ObjectSimilarity.objects.filter(
        object_1_content_type=ctype, object_2_content_type=ctype,
        object_1_id=obj_a.id, object_2_id=obj_b.pk).exists()


@pytest.mark.django_db
def test_instance_list():
    """Querysets/model managers have an instance_list method."""
    set_score = models.ObjectSimilarity.set  # Just a readability alias
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')
    obj_c = make_quote('Foobar')
    set_score(obj_a, obj_b, 1)
    set_score(obj_a, obj_c, 2)

    instances = models.ObjectSimilarity.objects.all().order_by(
        'score').get_instances_for(obj_a)
    assert [obj_b, obj_c] == list(instances)


@pytest.mark.django_db
def test_exclude_objects_qset():
    """ObjectSimilarity qset.exclude_objects can take a queryset."""
    set_score = models.ObjectSimilarity.set  # Just a readability alias
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')
    obj_c = make_quote('Foo')
    obj_d = make_quote('Bar')
    sim_b = set_score(obj_a, obj_b, 1)
    set_score(obj_a, obj_c, 2)
    sim_d = set_score(obj_a, obj_d, 3)

    sims = models.ObjectSimilarity.objects.all().order_by('score')
    sims = sims.exclude_objects(
        quotes.models.Quote.objects.filter(pk=obj_c.pk))

    assert [sim_b, sim_d] == list(sims)


@pytest.mark.django_db
def test_filter_objects():
    """ObjectSimilarity qset.filter_objects takes a queryset."""
    set_score = models.ObjectSimilarity.set  # Just a readability alias
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')
    obj_c = make_quote('Foo')
    obj_d = make_quote('Bar')
    sim_ab = set_score(obj_a, obj_b, 1)
    sim_ac = set_score(obj_a, obj_c, 2)
    sim_ad = set_score(obj_a, obj_d, 3)
    set_score(obj_b, obj_c, 5)  # This data that shouldn't be included
    set_score(obj_b, obj_d, 6)

    quote_a = quotes.models.Quote.objects.filter(pk=obj_a.pk)
    sims = models.ObjectSimilarity.objects.filter_objects(quote_a)
    sims = sims.order_by('score')

    assert [sim_ab, sim_ac, sim_ad] == list(sims)


@pytest.mark.django_db
def test_get_instances_fallback():
    """get_instances_for uses a callback when an instance is missing."""
    set_score = models.ObjectSimilarity.set  # Just a readability alias
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')
    obj_c = make_quote('Foobar')
    ctype = ct_models.ContentType.objects.get_for_model(obj_a)
    set_score(obj_a, obj_b, 1)
    set_score(obj_a, obj_c, 2)
    obj_b_pk = obj_b.pk  # .pk gets set to None after delete()
    obj_b.delete()
    handle_missing = mock.MagicMock()

    objs = models.ObjectSimilarity.objects.all().order_by(
        'score').get_instances_for(obj_a, handle_missing)

    assert 1 == handle_missing.call_count
    assert mock.call(ctype.pk, obj_b_pk) == handle_missing.call_args
    assert [obj_c] == list(objs)


@pytest.mark.django_db
def test_get_instances_default():
    """get_instances_for propagates ObjectDoesNotExist without a handler."""
    set_score = models.ObjectSimilarity.set  # Just a readability alias
    obj_a = make_quote('Hello')
    obj_b = make_quote('World')
    obj_c = make_quote('Foobar')
    set_score(obj_a, obj_b, 1)
    set_score(obj_a, obj_c, 2)
    obj_b.delete()

    with pytest.raises(quotes.models.Quote.DoesNotExist):
        models.ObjectSimilarity.objects.all().order_by(
            'score').get_instances_for(obj_a)
