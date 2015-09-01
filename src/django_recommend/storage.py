# coding: utf-8
"""Allow pyrecommend to read and write to the Django database."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import django.core.exceptions
from django.contrib.contenttypes import models as ct_models

import django_recommend
from . import conf
from . import models


LOG = logging.getLogger(__name__)


class ResultStorage(object):  # pylint: disable=too-few-public-methods
    """Write items to the Django database."""

    def __setitem__(self, key, val):
        models.ObjectSimilarity.set(*key, score=val)
        LOG.debug('Setting %s to %s', key, val)


def get_object(ctype_id, obj_id):
    """Get a model from a ContentType and an object ID."""
    ctype = ct_models.ContentType.objects.get(pk=ctype_id)
    return ctype.model_class().objects.get(pk=obj_id)


class ObjectData(object):  # pylint: disable=too-few-public-methods
    """Allow pyrecommend to read Django ORM objects."""

    def __init__(self, obj):
        self.obj = obj

    def keys(self):
        """All objects worth considering."""
        return list(iter(self))

    def __getitem__(self, item):
        """Get all scores for a particular object."""
        return django_recommend.scores_for(item)

    def __iter__(self):
        ctype = ct_models.ContentType.objects.get_for_model(self.obj)

        # Get all users who rated this object
        relevant_users = models.UserScore.objects.filter(
            object_content_type=ctype, object_id=self.obj.pk
        ).values_list('user', flat=True).distinct()

        # Get all objects that those users have rated
        relevant_objects = models.UserScore.objects.filter(
            user__in=relevant_users
        ).values_list(
            'object_content_type', 'object_id'
        ).distinct()

        for args in relevant_objects:
            try:
                yield get_object(*args)
            except django.core.exceptions.ObjectDoesNotExist:
                if conf.settings.RECOMMEND_PURGE_MISSING_DATA:
                    django_recommend.forget_object(*args)
                else:
                    raise
