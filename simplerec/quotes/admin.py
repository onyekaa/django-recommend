"""/admin/ config for the quotes app."""
# pylint: disable=missing-docstring
from django.contrib import admin

from . import models


@admin.register(models.Quote)
class QuoteAdmin(admin.ModelAdmin):
    pass
