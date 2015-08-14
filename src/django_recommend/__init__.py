# coding: utf-8
"""Utility/high-level functions for interacting with suggestions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.contenttypes import models as ct_models


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
    return models.UserScore.set(user, obj, score)


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
    return models.UserScore.setdefault(user, obj, score)


def scores_for(obj):
    """Get all scores for the given object."""
    from . import models
    return models.UserScore.scores_for(obj)


def get_score(user, obj):
    """Get a user's score for the given object."""
    from . import models
    return models.UserScore.get(user, obj)


def similar_objects(obj):
    """Get objects most similar to obj.

    Returns an iterator, not a collection.

    """
    from . import models

    ctype = ct_models.ContentType.objects.get_for_model(obj)

    criteria = {
        'object_1_content_type': ctype,
        'object_1_id': obj.pk
    }

    high_similarity = models.ObjectSimilarity.objects.filter(
        **criteria).order_by('-score').prefetch_related(
            'object_1_content_type', 'object_2_content_type')

    return (ctype.get_object_for_this_type(pk=s.object_2_id) for s in
            high_similarity)
