# coding: utf-8
"""Tasks for recommendations."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pyrecommend.similarity
from django.contrib.contenttypes import models as ct_models

from . import storage


def signal_handler(sender, **kwargs):
    """Kickoff the update similarity calculation below.

    This will figure out what asynchronous method is most appropriate to use.
    (E.g. celery, or if debugging Python threads, etc.)

    """


def update_similarity(obj_params):
    """Update similarity scores for object and all related objects.

    obj_params: a tuple of (object_id, object_content_type_id).

    """
    obj_id, ctype_id = obj_params
    content_type = ct_models.ContentType.objects.get(pk=ctype_id)
    obj = content_type.get_object_for_this_type(pk=obj_id)
    obj_data = storage.ObjectData(obj)

    sim_func = pyrecommend.similarity.dot_product

    pyrecommend.calculate_similarity(obj_data, sim_func,
                                     storage.ResultStorage())
