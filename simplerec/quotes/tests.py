"""Tests for the Quotes app."""
import pytest
from django.core import exceptions

from . import models


@pytest.mark.django_db
def test_quote_similarity_pk_order():
    """Pairs of quotes must be ordered by PK."""

    # Small/big in terms of their IDs.
    small_quote = models.Quote.objects.create(content='foo', pk=500)
    big_quote = models.Quote.objects.create(content='bar', pk=505)

    # Wrong order raises an exception.
    with pytest.raises(exceptions.ValidationError):
        models.QuoteSimilarity.objects.create(
            quote_1=big_quote, quote_2=small_quote, score=0.3)

    # Good order works fine.
    models.QuoteSimilarity.objects.create(
        quote_1=small_quote, quote_2=small_quote, score=0.3)


@pytest.mark.django_db
class TestQuoteSimilarityStore(object):
    """QuoteSimilarity.store sorts out which quote gets which number."""

    @pytest.fixture(autouse=True)
    def make_quotes(self):
        """Create small/big quote."""
        # pylint: disable=attribute-defined-outside-init
        self.small_quote = models.Quote.objects.create(content='foo', pk=500)
        self.big_quote = models.Quote.objects.create(content='bar', pk=505)

    def test_from_scratch(self):
        """Will create a new QuoteSimilarity instance properly."""
        inst, created = models.QuoteSimilarity.store(
            self.big_quote, self.small_quote, 0.3)

        assert created
        assert inst.quote_1 == self.small_quote
        assert inst.quote_2 == self.big_quote
        assert inst.score == 0.3

    def test_updates_existing(self):
        """If an existing score is found, updates that instance."""
        sim_score = models.QuoteSimilarity.objects.create(
            quote_1=self.small_quote, quote_2=self.big_quote, score=0.4)

        inst, created = models.QuoteSimilarity.store(
            self.big_quote, self.small_quote, 0.9)

        assert not created
        assert inst.pk == sim_score.pk
        assert inst.quote_1 == self.small_quote
        assert inst.quote_2 == self.big_quote
        assert inst.score == 0.9
