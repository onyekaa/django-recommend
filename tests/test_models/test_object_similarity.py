# coding: utf-8
"""Tests for ObjectSimilarity."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from django.contrib.contenttypes import models as ct_models

from django_recommend import models
from quotes import models as quote_models


def make_quote(content, **kwargs):
    """Shorthand for the Quote constructor."""
    return quote_models.Quote.objects.create(content=content, **kwargs)


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
