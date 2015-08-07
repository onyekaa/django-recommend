"""/admin/ config for the quotes app."""
# pylint: disable=missing-docstring
from django.contrib import admin

from . import models


@admin.register(models.Quote)
class QuoteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.FavoriteQuote)
class FavoriteQuoteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ViewedQuote)
class ViewedQuoteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.AnonymousViewedQuote)
class AnonymousViewedQuoteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.QuoteSimilarity)
class QuoteSimilarityAdmin(admin.ModelAdmin):
    list_display = ('score', 'quote_1', 'quote_2')
