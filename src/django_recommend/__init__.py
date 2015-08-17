# coding: utf-8
"""Utility/high-level functions for interacting with suggestions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.db.models
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
    Q = django.db.models.Q  # pylint: disable=invalid-name

    ctype = ct_models.ContentType.objects.get_for_model(obj)

    lookup = ((Q(object_1_content_type=ctype) & Q(object_1_id=obj.pk)) |
              (Q(object_2_content_type=ctype) & Q(object_2_id=obj.pk)))

    high_similarity = models.ObjectSimilarity.objects.filter(lookup)
    high_similarity = high_similarity.order_by('-score').prefetch_related(
        'object_1_content_type', 'object_2_content_type')

    def get_other_object(sim_obj):
        """Get the object in sim_obj that isn't obj."""
        same_id_as_1 = sim_obj.object_1_id == obj.pk
        same_ctype_as_1 = sim_obj.object_1_content_type == ctype

        if same_id_as_1 and same_ctype_as_1:
            return sim_obj.object_2
        return sim_obj.object_1

    return (get_other_object(s) for s in high_similarity)
