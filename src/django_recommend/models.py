# coding: utf-8
"""Models for item-to-item collaborative filtering."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ObjectSimilarity(models.Model):
    """Similarity between two Django objects."""
    object_1_id = models.IntegerField()
    object_1_content_type = models.ForeignKey(ContentType)
    object_1 = GenericForeignKey('object_1_content_type', 'object_1_id')

    object_2_id = models.IntegerField()
    object_2_content_type = models.ForeignKey(ContentType)
    object_2 = GenericForeignKey('object_2_content_type', 'object_2_id')

    # The actual similarity rating
    score = models.FloatField()

    class Meta:
        unique_together = (
            'object_1_id', 'object_1_content_type',
            'object_2_id', 'object_2_content_type')
