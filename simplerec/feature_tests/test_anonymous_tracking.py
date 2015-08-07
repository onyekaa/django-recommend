# coding: utf-8
"""Test that anonymous users are tracked."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import quotes.models


@pytest.mark.django_db
def test_anonymous_views_quote(client, live_server):
    """Anonymous views to quotes get tracked."""
    def num_anonymous_views():
        return quotes.models.AnonymousViewedQuote.objects.count()

    def visit(quote):
        client.get(live_server.url + quote.get_absolute_url())

    quote_1 = quotes.models.Quote.objects.create(
        content='Test quote')
    quote_2 = quotes.models.Quote.objects.create(
        content='Test quote 2')

    assert num_anonymous_views() == 0

    # A single view gets tracked
    visit(quote_1)
    assert num_anonymous_views() == 1

    # Repeat views do not get tracked
    visit(quote_1)
    assert num_anonymous_views() == 1

    # Viewing a different quote gets tracked
    visit(quote_2)
    assert num_anonymous_views() == 2
