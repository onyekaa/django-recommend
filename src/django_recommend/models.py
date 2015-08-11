# coding: utf-8
"""Models for item-to-item collaborative filtering."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class ObjectSimilarity(models.Model):  # pylint: disable=model-missing-unicode
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

    def __str__(self):

        # On Python 2, str() will convert it back to a bytestr.
        return str('{}, {}: {}').format(self.object_1_id, self.object_2_id,
                                        self.score)


class UserScore(models.Model):
    """Store a user's rating of an object.

    "Rating" doesn't necessarily need to be e.g. 1-10 points or 1-5 star voting
    system. It is often easy to treat e.g. object view as 1 point and object
    bookmarking as 5 points, for example. This is called 'implicit feedback.'

    """
    object_id = models.IntegerField()
    object_content_type = models.ForeignKey(ContentType)
    object = GenericForeignKey('object_content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    score = models.FloatField()

    class Meta:
        unique_together = ('object_id', 'object_content_type', 'user')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(UserScore, self).save(*args, **kwargs)
