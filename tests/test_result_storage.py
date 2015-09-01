# coding: utf-8
"""Tests for result storage."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest
from django.contrib.contenttypes import models as ct_models

import django_recommend.models
import django_recommend.storage
import quotes.models


@pytest.mark.django_db
def test_store_results():
    """ResultStorage creates QuoteSimilarity objects."""
    make_quote = quotes.models.Quote.objects.create

    # Specify PKs so quote_a will be object_1
    quote_a = make_quote(content='Hello', pk=20)
    quote_b = make_quote(content='World', pk=25)
    ctype = ct_models.ContentType.objects.get_for_model(quote_a)

    assert not django_recommend.models.ObjectSimilarity.objects.filter(
        object_1_id=quote_a.pk, object_1_content_type=ctype,
        object_2_id=quote_b.pk, object_2_content_type=ctype).exists()

    storage = django_recommend.storage.ResultStorage()
    storage[(quote_a, quote_b)] = 5

    assert django_recommend.models.ObjectSimilarity.objects.filter(
        object_1_id=quote_a.pk, object_1_content_type=ctype,
        object_2_id=quote_b.pk, object_2_content_type=ctype).exists()
