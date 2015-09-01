# coding: utf-8
"""Models for item-to-item collaborative filtering."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core import exceptions
from django.db import models
from django.db.models import signals as model_signals
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible

import django_recommend
from . import conf


NO_RELATED_NAME = '+'  # Try to clarify obscure Django syntax.


def respect_purge_setting(*args):
    """Raise or delete related objects based on settings.

    This is a when_missing handler for
    ObjectSimilarityQueryset.get_instances_for.

    """
    if conf.settings.RECOMMEND_PURGE_MISSING_DATA:
        django_recommend.forget_object(*args)
    else:
        raise


class ObjectSimilarityQueryset(models.QuerySet):
    """The custom manager used for the ObjectSimilarity class."""

    def get_instances_for(self, obj, when_missing=respect_purge_setting):
        """Get the instances in this queryset that are not `obj`.

        Returns a list.

        when_missing:
            a callback function to execute when an instance that should be
            suggested is not present in the database (i.e. get() raises
            ObjectDoesNotExist). This function will be called with two
            parameters: the content type id, and the object id.

            The default callback propagates the underlying ObjectDoesNotExist
            exception.

            If this method does not raise an exception, the triggering object
            is simply ignored and not included in the result list. For this
            reason it's possible for a queryset of 5 objects to only return,
            say, 4 instances, if one of the objects referred to in an
            ObjectSimilarity is in fact no longer present in the database.

        """
        ctype = ContentType.objects.get_for_model(obj)

        def get_object_from_ctype(contenttype, target_id):
            """The builtin method of doing this breaks with multiple DBs."""
            return contenttype.model_class().objects.get(pk=target_id)

        def get_object_params(sim_obj, num):
            """Get the content_type and PK of an object from sim_obj."""
            prefix = 'object_{}_'.format(num)
            target_id = getattr(sim_obj, prefix + 'id')
            target_ctype = getattr(sim_obj, prefix + 'content_type')
            return target_ctype, target_id

        def get_other_object_params(sim_obj):
            """Get the content type and pk of the other object in sim_obj."""
            same_id_as_1 = sim_obj.object_1_id == obj.pk
            same_ctype_as_1 = sim_obj.object_1_content_type == ctype

            if same_id_as_1 and same_ctype_as_1:
                return get_object_params(sim_obj, 2)
            return get_object_params(sim_obj, 1)

        instances = []
        for sim in self:
            other_ctype, other_pk = get_other_object_params(sim)
            try:
                inst = get_object_from_ctype(other_ctype, other_pk)
            except exceptions.ObjectDoesNotExist:
                when_missing(other_ctype.pk, other_pk)
            else:
                instances.append(inst)
        return instances

    def __build_query(self, qset):
        """Get a lookup to match qset objects as either object_1 or object_2.

        qset is any Django queryset.

        """
        model = qset.model
        ctype = ContentType.objects.get_for_model(model)

        # Prevent cross-db joins
        if qset.db != self.db:
            ids = qset.values_list('id', flat=True)

            # Forces the DB query to happen early
            qset = list(ids)

        lookup = ((Q(object_1_content_type=ctype) & Q(object_1_id__in=qset)) |
                  (Q(object_2_content_type=ctype) & Q(object_2_id__in=qset)))
        return lookup

    def exclude_objects(self, qset):
        """Exclude all similarities that include the given objects.

        qset is a queryset of model instances to exclude. These should be the
        types of objects stored in ObjectSimilarity/UserScore, **not**
        ObjectSimilarity/UserScore themselves.

        """
        return self.exclude(self.__build_query(qset))

    def filter_objects(self, qset):
        """Find all similarities that include the given objects.

        qset is a queryset of model instances to include. These should be the
        types of objects stored in ObjectSimilarity/UserScore, **not**
        ObjectSimilarity/UserScore themselves.

        """
        return self.filter(self.__build_query(qset))


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

    objects = ObjectSimilarityQueryset.as_manager()

    class Meta:
        index_together = (
            ('object_1_id', 'object_1_content_type'),
            ('object_2_id', 'object_2_content_type'),
        )

        ordering = ['-score']

        unique_together = (
            'object_1_id', 'object_1_content_type', 'object_2_id',
            'object_2_content_type',
        )

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

        inst_lookup = dict(
            object_1_content_type=ContentType.objects.get_for_model(obj_1),
            object_1_id=obj_1.pk,
            object_2_content_type=ContentType.objects.get_for_model(obj_2),
            object_2_id=obj_2.pk,
        )

        # Save space by not storing scores of 0.
        if score == 0:
            ObjectSimilarity.objects.filter(**inst_lookup).delete()
            sim = None
        else:
            kwargs = dict(inst_lookup)
            kwargs['defaults'] = {'score': score}
            sim, _ = ObjectSimilarity.objects.update_or_create(**kwargs)

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

    user = models.CharField(max_length=255, db_index=True)

    score = models.FloatField()

    class Meta:
        index_together = ('object_id', 'object_content_type')
        unique_together = ('object_id', 'object_content_type', 'user')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(UserScore, self).save(*args, **kwargs)

    @classmethod
    def __user_str(cls, user_or_str):
        """Coerce user_or_str params into a string."""
        try:
            user_id = user_or_str.pk
        except AttributeError:
            return user_or_str
        return 'user:{}'.format(user_id)

    @classmethod
    def set(cls, user_or_str, obj, score):
        """Store the score for the given user and given object.

        Returns the created UserScore instance.

        """
        user = cls.__user_str(user_or_str)
        ctype = ContentType.objects.get_for_model(obj)

        inst_lookup = dict(
            user=user, object_id=obj.pk, object_content_type=ctype)

        if score:
            kwargs = dict(inst_lookup)
            kwargs['defaults'] = {'score': score}
            inst, _ = cls.objects.update_or_create(**kwargs)
        else:
            inst = None
            cls.objects.filter(**inst_lookup).delete()
        return inst

    @classmethod
    def setdefault(cls, user_or_str, obj, score):
        """Store the user's score only if there's no existing score."""
        user = cls.__user_str(user_or_str)
        ctype = ContentType.objects.get_for_model(obj)
        cls.objects.get_or_create(
            user=user, object_id=obj.pk, object_content_type=ctype,
            defaults={'score': score}
        )

    @classmethod
    def get(cls, user_or_str, obj):
        """Get the score that user gave to obj.

        Returns the actual score value, not the UserScore instance.

        "Unrated" objects return 0.

        """
        user = cls.__user_str(user_or_str)
        ctype = ContentType.objects.get_for_model(obj)
        try:
            inst = cls.objects.get(user=user, object_id=obj.pk,
                                   object_content_type=ctype)
            return inst.score
        except cls.DoesNotExist:
            return 0

    @classmethod
    def scores_for(cls, obj):
        """Get all scores for the given object.

        Returns a dictionary, not a queryset.

        """
        ctype = ContentType.objects.get_for_model(obj)
        scores = cls.objects.filter(object_content_type=ctype,
                                    object_id=obj.pk)
        return {score.user: score.score for score in scores}

    def __str__(self):
        return '{}, {}: {}'.format(self.user, self.object_id, self.score)


def call_handler(*args, **kwargs):
    """Proxy for the signal handler defined in tasks.

    Prevents a circular import problem.

    """
    from . import tasks
    tasks.signal_handler(*args, **kwargs)


model_signals.post_save.connect(call_handler, UserScore,
                                dispatch_uid="recommend_post_save")
model_signals.post_delete.connect(call_handler, UserScore,
                                  dispatch_uid="recommend_post_save")
