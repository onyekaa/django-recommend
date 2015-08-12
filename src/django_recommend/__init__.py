# coding: utf-8
"""Utility/high-level functions for interacting with suggestions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def set_score(request_or_user, obj, score):
    """Set the score for the given obj.

    Will attribute it to the user, if request has an authenticated user, or to
    a session.

    """
    from . import models
    try:  # Requests have a .user object
        user = request_or_user.user
    except AttributeError:  # Probably not a request
        user = request_or_user
    models.UserScore.set(user, obj, score)


def setdefault_score(request_or_user, obj, score):
    """Set the score for the given obj if it doesn't exist.

    Will attribute it to the user, if request has an authenticated user, or to
    a session.

    """
    from . import models
    try:  # Requests have a .user object
        user = request_or_user.user
    except AttributeError:  # Probably not a request
        user = request_or_user
    models.UserScore.setdefault(user, obj, score)


def scores_for(obj):
    """Get all scores for the given object."""
    from . import models
    return models.UserScore.scores_for(obj)


def get_score(user, obj):
    """Get a user's score for the given object."""
    from . import models
    return models.UserScore.get(user, obj)
