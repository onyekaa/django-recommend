# coding: utf-8
"""Allow pyrecommend to read and write to the Django database."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.contenttypes import models as ct_models

from . import models


class ResultStorage(object):  # pylint: disable=too-few-public-methods
    """Write items to the Django database."""

    def __setitem__(self, key, val):
        models.ObjectSimilarity.set(*key, score=val)


def get_object(ctype_id, obj_id):
    """Get a model from a ContentType and an object ID."""
    ctype = ct_models.ContentType.objects.get(pk=ctype_id)
    return ctype.get_object_for_this_type(pk=obj_id)


class ObjectData(object):
    """Allow pyrecommend to read Django ORM objects."""

    def __init__(self, obj):
        self.obj = obj

    def keys(self):
        """All objects worth considering."""
        ctype = ct_models.ContentType.objects.get_for_model(self.obj)

        # Get all users who rated this object
        relevant_users = models.UserScore.objects.filter(
            object_content_type=ctype, object_id=self.obj.pk
        ).values_list('user', flat=True).distinct()

        # Get all objects that those users have rated
        relevant_objects = models.UserScore.objects.filter(
            user__in=relevant_users
        ).values_list('object_content_type', 'object_id')

        return [get_object(*args) for args in relevant_objects]
