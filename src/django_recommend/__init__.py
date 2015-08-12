# coding: utf-8
"""Utility/high-level functions for interacting with suggestions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import models


def set_score(request, obj, score):
    """Set the score for the given obj.

    Will attribute it to the user, if request has an authenticated user, or to
    a session.

    """
    user = request.user
    models.UserScore.set(user, obj, score)


def scores_for(obj):
    """Get all scores for the given object."""
    return models.UserScore.scores_for(obj)
