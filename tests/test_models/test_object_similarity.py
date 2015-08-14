# coding: utf-8
"""Tests for ObjectSimilarity."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

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
