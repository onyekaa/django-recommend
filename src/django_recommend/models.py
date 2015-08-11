# coding: utf-8
"""Models for item-to-item collaborative filtering."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models


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

    def clean(self):
        if (self.object_1_id == self.object_2_id and
                self.object_1_content_type == self.object_2_content_type):
            raise ValidationError('An object cannot be similar to itself.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ObjectSimilarity, self).save(*args, **kwargs)
