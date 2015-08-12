# coding: utf-8
"""Interface between pyrecommend and Django quote app."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections

import django.contrib.auth.models  # pylint: disable=unused-import
import pyrecommend.similarity
from django.contrib import auth  # NOTE: auth.models is used, needs above
from django.db.models import Q

import django_recommend
import quotes.models


class QuoteData(object):  # pylint: disable=too-few-public-methods
    """Provide access to quote data to recommendation algorithm."""

    def __init__(self, quote):
        self.quote = quote

    @property
    def items(self):
        """Get all quotes that are somehow related to this quote."""
        quote = self.quote

        # Get all users who viewed or favorited this quote
        relevant_users = auth.models.User.objects.filter(
            Q(favoritequote__quote=quote) | Q(viewedquote__quote=quote)
        ).distinct()

        # Get all sessions that have viewed this quote
        relevant_sessions = (quotes.models.AnonymousViewedQuote.objects
                             .filter(quote=quote)
                             .values_list('session_key', flat=True).distinct())

        # Get all quotes that said users have viewed or favorited (will
        # include 'quote')
        relevant_quotes = quotes.models.Quote.objects.filter(
            Q(favoritequote__user__in=relevant_users) |
            Q(viewedquote__user__in=relevant_users) |
            Q(anonymousviewedquote__session_key__in=relevant_sessions)
        ).distinct()

        return relevant_quotes.prefetch_related(
            'viewedquote_set', 'favoritequote_set', 'anonymousviewedquote_set')

    def __getitem__(self, quote):
        """Get all user ratings for this quote."""
        return collections.defaultdict(
            lambda: 0, django_recommend.scores_for(quote))

    def __iter__(self):
        return iter(self.items)


class ResultStorage(object):  # pylint: disable=too-few-public-methods
    """Write scores into the database."""

    @classmethod
    def __setitem__(cls, quote, similarity_scores):
        for score, other_quote in similarity_scores:
            quotes.models.QuoteSimilarity.store(quote, other_quote, score)


def turn_to_pks(sim_data):
    """Change a similarity data dictionary to use PKs instead of models.

    This makes it slightly easier to read data when futzing with the shell.

    """
    return {key.pk: [(score, quote.pk) for score, quote in val]
            for key, val in sim_data.items()}


def update_suggestions(quote):
    """Update suggestion info for quote and all related quotes."""
    pyrecommend.calculate_similarity(
        QuoteData(quote), pyrecommend.similarity.dot_product, ResultStorage())
