# coding: utf-8
"""Views for quotes."""
# pylint: disable=too-many-ancestors
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.views import generic
from django.views.generic import detail

from . import models


class QuoteIndex(generic.ListView):
    """Show all quotes in the system."""
    queryset = models.Quote.objects.all()


class QuoteDetail(generic.DetailView):
    """Show a single quote."""
    queryset = models.Quote.objects.all()

    def get_object(self, *args, **kwargs):
        quote = super(QuoteDetail, self).get_object(*args, **kwargs)
        user = self.request.user
        if user.is_authenticated():
            quote.is_favorited = quote.is_favorited_by(user)
        else:
            quote.is_favorited = False
        return quote

    def get(self, *args, **kwargs):
        """Track views."""
        resp = super(QuoteDetail, self).get(*args, **kwargs)
        quote = self.get_object()
        if self.request.user.is_authenticated():
            quote.mark_viewed_by(self.request.user)
        else:
            sess_key = self.request.session.session_key
            if sess_key:
                quote.mark_viewed_by_anonymous(sess_key)
        return resp


class MarkQuoteFavorite(detail.SingleObjectMixin, generic.RedirectView):
    """Mark a single quote as favorite and redirect to its detail."""

    permanent = False

    queryset = models.Quote.objects.all()

    def get_redirect_url(self, *args, **kwargs):
        return self.get_object().get_absolute_url()

    # pylint: disable=missing-docstring
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            quote = self.get_object()
            quote.mark_favorite_for(user)
        return super(MarkQuoteFavorite, self).get(request, *args, **kwargs)


class UnfavoriteQuote(detail.SingleObjectMixin, generic.RedirectView):
    """Mark a single quote as favorite and redirect to its detail."""

    permanent = False

    queryset = models.Quote.objects.all()

    def get_redirect_url(self, *args, **kwargs):
        return self.get_object().get_absolute_url()

    # pylint: disable=missing-docstring
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            quote = self.get_object()
            quote.unmark_favorite_for(user)
        return super(UnfavoriteQuote, self).get(request, *args, **kwargs)
