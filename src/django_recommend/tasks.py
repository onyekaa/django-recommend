# coding: utf-8
"""Tasks for recommendations."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyrecommend.similarity

from . import models


def update_similarity(obj_params):
    """Update similarity scores for object and all related objects.

    obj_params: a tuple of (object_id, object_content_type_id).

    """
    obj_id, ctype_id = obj_params
    users_rated_object = models.UserScore.objects.none().exclude(
        object_id=obj_id, object_content_type__id=ctype_id)
    assert not users_rated_object
    sim_func = pyrecommend.similarity.dot_product
    pyrecommend.calculate_similarity({}, sim_func, {})
