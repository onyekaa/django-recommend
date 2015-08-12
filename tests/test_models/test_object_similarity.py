# coding: utf-8
"""Tests for ObjectSimilarity."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from django_recommend import models
from quotes import models as quote_models


@pytest.mark.django_db
def test_set_bad_order():
    """ObjectSimilarity.set() always stores in the same order."""
    make_quote = quote_models.Quote.objects.create
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
