# coding: utf-8
"""Models for quote stuff."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import threading
import time

from django.conf import settings
from django.core import exceptions
from django.core import urlresolvers
from django.db import models
from django.db.models import Q
from django.db.models import signals

import get_ratings


LOG = logging.getLogger(__name__)


class Quote(models.Model):
    """Some text that someone finds memorable."""

    content = models.CharField(max_length=400, unique=True)

    def get_absolute_url(self):
        """Get a URL to this quote's detail page."""
        return urlresolvers.reverse('quotes-detail', kwargs={'pk': self.pk})

    def mark_viewed_by(self, user):
        """Record that the given Django user viewed this quote."""
        ViewedQuote.objects.get_or_create(user=user, quote=self)

    def mark_viewed_by_anonymous(self, session_key):
        """Record a non-authenticated user viewed this quote."""
        AnonymousViewedQuote.objects.get_or_create(
            session_key=session_key, quote=self)

    def is_favorited_by(self, user):
        """Check if user has favorited this quote."""
        return FavoriteQuote.objects.filter(user=user, quote=self).exists()

    def mark_favorite_for(self, user):
        """Mark this as a favorite quote for user."""
        FavoriteQuote.objects.get_or_create(user=user, quote=self)

    def unmark_favorite_for(self, user):
        """Remove favorite mark for the given user."""
        FavoriteQuote.objects.filter(user=user, quote=self).delete()

    @property
    def similar_quotes(self, limit=5):
        """A QuerySet of the most similar quotes."""
        sim_quotes = QuoteSimilarity.objects.filter(
            Q(quote_1=self) | Q(quote_2=self)).distinct()
        sim_quotes = sim_quotes.order_by('-score')
        if limit:
            sim_quotes = sim_quotes[:limit]

        def other_quote(sim):
            """Get the non-self Quote from a QuoteSimilarity."""
            is_q1 = sim.quote_1 == self
            return sim.quote_2 if is_q1 else sim.quote_1

        return [other_quote(s) for s in sim_quotes]

    def __unicode__(self):
        return self.content


class FavoriteQuote(models.Model):
    """Track when a user 'favorites' a particular quote."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        star_symbol = '\u2605'
        return '{} {}: {}'.format(star_symbol, self.user, self.quote)

    class Meta:
        unique_together = ('user', 'quote')


class ViewedQuote(models.Model):
    """Track when a user views a quote."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        checkmark = '\u2713'
        return '{} {}: {}'.format(checkmark, self.user, self.quote)

    class Meta:
        unique_together = ('user', 'quote')


class AnonymousViewedQuote(models.Model):
    """Track when an anonymous user views a quote."""
    session_key = models.CharField(max_length=255)

    quote = models.ForeignKey(Quote)

    def __unicode__(self):
        checkmark = '\u2713'
        return '{} {}: {}'.format(checkmark, self.session_key, self.quote)

    class Meta:
        unique_together = ('session_key', 'quote')


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


# Trigger suggestion calculations when tracking info updates.
signals.post_save.connect(update_suggestions_handler,
                          sender=AnonymousViewedQuote)
signals.post_save.connect(update_suggestions_handler, sender=ViewedQuote)
signals.post_save.connect(update_suggestions_handler, sender=FavoriteQuote)
signals.post_delete.connect(update_suggestions_handler, sender=FavoriteQuote)


NO_RELATED_NAME = '+'  # Try to clarify obscure Django syntax.


class QuoteSimilarity(models.Model):
    """Record similarity between a pair of quotes.

    To prevent duplicate data, e.g. storing (a, b, 0.5) as well as
    (b, a, 0.5), quote_1 should always contain the quote with the smaller PK.
    This has no real meaning but ensures there is only one unique way any pair
    of quotes can be stored in this model.

    """

    quote_1 = models.ForeignKey(Quote, related_name=NO_RELATED_NAME)

    quote_2 = models.ForeignKey(Quote, related_name=NO_RELATED_NAME)

    score = models.FloatField()

    def clean(self):
        """Ensure quote_1's pk is smaller than quote_2's."""
        if self.quote_1.pk > self.quote_2.pk:
            raise exceptions.ValidationError(
                'quote_1 must have the smaller pk.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(QuoteSimilarity, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'QuoteSimilarity(quote_1={}, quote_2={}, score={})'.format(
            self.quote_1.pk, self.quote_2.pk, self.score)

    @classmethod
    def store(cls, quote_a, quote_b, score):
        """Utility to create new QuoteSimilarity objects.

        Figures out the valid unique order for quote_a and quote_b.

        """
        if quote_a.pk < quote_b.pk:
            quote_1, quote_2 = quote_a, quote_b
        else:
            quote_1, quote_2 = quote_b, quote_a

        if score:
            return cls.objects.update_or_create(
                quote_1=quote_1, quote_2=quote_2, defaults={'score': score})
        else:
            cls.objects.filter(quote_1=quote_1, quote_2=quote_2).delete()
            return False, None

    class Meta:
        unique_together = ('quote_1', 'quote_2')
        verbose_name_plural = 'Quote similarities'
