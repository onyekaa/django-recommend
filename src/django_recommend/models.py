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


NO_RELATED_NAME = '+'  # Try to clarify obscure Django syntax.


@python_2_unicode_compatible
class ObjectSimilarity(models.Model):  # pylint: disable=model-missing-unicode
    """Similarity between two Django objects."""
    object_1_id = models.IntegerField()
    object_1_content_type = models.ForeignKey(ContentType,
                                              related_name=NO_RELATED_NAME)
    object_1 = GenericForeignKey('object_1_content_type', 'object_1_id')

    object_2_id = models.IntegerField()
    object_2_content_type = models.ForeignKey(ContentType,
                                              related_name=NO_RELATED_NAME)
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

    @classmethod
    def set(cls, obj_a, obj_b, score):
        """Set the similarity between obj_a and obj_b to score.

        Returns the created ObjectSimilarity instance.

        """

        # Always store the lower PKs as object_1, so the pair
        # (object_1, object_2) has a distinct ordering, to prevent duplicate
        # data.

        def sort_key(obj):
            """Get a sortable tuple representing obj."""
            return (ContentType.objects.get_for_model(obj).pk, obj.pk)

        obj_a_key = sort_key(obj_a)
        obj_b_key = sort_key(obj_b)

        if obj_a_key < obj_b_key:
            obj_1, obj_2 = obj_a, obj_b
        else:
            obj_1, obj_2 = obj_b, obj_a

        sim = ObjectSimilarity.objects.create(
            object_1_content_type=ContentType.objects.get_for_model(obj_1),
            object_1_id=obj_1.pk,
            object_2_content_type=ContentType.objects.get_for_model(obj_2),
            object_2_id=obj_2.pk,
            score=score)

        return sim

    def __str__(self):
        return '{}, {}: {}'.format(self.object_1_id, self.object_2_id,
                                   self.score)


@python_2_unicode_compatible
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

    @classmethod
    def set(cls, user, obj, score):
        """Store the score for the given user and given object."""
        ctype = ContentType.objects.get_for_model(obj)
        cls.objects.create(user=user, object_id=obj.pk,
                           object_content_type=ctype, score=score)

    @classmethod
    def scores_for(cls, obj):
        """Get all scores for the given object.

        Returns a dictionary, not a queryset.

        """
        ctype = ContentType.objects.get_for_model(obj)
        scores = cls.objects.filter(object_content_type=ctype,
                                    object_id=obj.pk)
        return {'user:{}'.format(score.user.pk): score.score
                for score in scores}

    def __str__(self):
        return '{}, {}: {}'.format(
            self.user.username, self.object_id, self.score)
