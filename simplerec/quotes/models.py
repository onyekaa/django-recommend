# coding: utf-8
"""Models for quote stuff."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import threading
import time

import django_recommend
from django.core import urlresolvers
from django.db import models


LOG = logging.getLogger(__name__)


class Quote(models.Model):
    """Some text that someone finds memorable."""

    content = models.CharField(max_length=400, unique=True)

    def get_absolute_url(self):
        """Get a URL to this quote's detail page."""
        return urlresolvers.reverse('quotes-detail', kwargs={'pk': self.pk})

    def mark_viewed_by(self, user):
        """Record that the given Django user viewed this quote."""
        django_recommend.setdefault_score(user, self, 1)

    def mark_viewed_by_anonymous(self, session_key):
        """Record a non-authenticated user viewed this quote."""
        django_recommend.setdefault_score(session_key, self, 1)

    def is_favorited_by(self, user):
        """Check if user has favorited this quote."""
        return django_recommend.get_score(user, self) == 5

    def mark_favorite_for(self, user):
        """Mark this as a favorite quote for user."""
        django_recommend.set_score(user, self, 5)

    def unmark_favorite_for(self, user):
        """Remove favorite mark for the given user."""
        django_recommend.set_score(user, self, 1)

    @property
    def similar_quotes(self):
        """A QuerySet of the most similar quotes."""
        return ['NOT YET IMPLEMENTED']

    def __unicode__(self):
        return self.content


def update_suggestions_handler(*_, **kwargs):
    """A signal handler to update a quote's suggestion data."""
    instance = kwargs['instance']

    # Uses a separated thread with a delay because some data seems to be in an
    # inconsistent state when run in the handler (e.g. non-nullable fields are
    # NULL). This may just be a SQLite quirk of some kind, however.
    delay = 1

    def do_it(quote_id):
        """Update 'similar quotes' data."""
        time.sleep(delay)  # Give DB time to update
        quote = Quote.objects.get(pk=quote_id)
        logger = logging.getLogger(__name__)
        try:
            quote = Quote.objects.get(pk=quote_id)
        except Quote.DoesNotExist:
            print("Couldn't find quote with ID", quote_id)
            return
        logger.info('Updating suggestions for quote %s', quote_id)
        get_ratings.update_suggestions(quote)

    LOG.info('Kicking off suggestions calc in %ss.', delay)
    proc = threading.Thread(target=do_it, args=(instance.quote.pk,))
    proc.start()
