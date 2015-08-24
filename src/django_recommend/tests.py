# coding: utf-8
"""Unit tests for the django_recommend app."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from . import models


def get_unicode(obj):
    """A Py2/Py3 compatible way to get a unicode string for an object."""
    try:
        func = unicode
    except NameError:  # pragma: no cover
        func = str  # Py3's str() is same as Py2's unicode()
    return func(obj)


class ObjectSimilarityTest(TestCase):
    """Tests for the ObjectSimilarity model."""

    def setUp(self):
        self.ctype_a = ContentType.objects.create(app_label='foo')
        self.ctype_b = ContentType.objects.create(app_label='bar')

    def test_duplicate_similarities(self):
        """Duplicate similarities can't be created."""

        # Creating one should work OK
        models.ObjectSimilarity.objects.create(
            object_1_id=1, object_1_content_type=self.ctype_a,
            object_2_id=1, object_2_content_type=self.ctype_b,
            score=3)

        # Creating the second should not (even with a different score)
        with self.assertRaises(ValidationError):
            models.ObjectSimilarity.objects.create(
                object_1_id=1, object_1_content_type=self.ctype_a,
                object_2_id=1, object_2_content_type=self.ctype_b,
                score=4)

        with self.assertRaises(IntegrityError):
            models.ObjectSimilarity.objects.bulk_create([
                models.ObjectSimilarity(
                    object_1_id=1, object_1_content_type=self.ctype_a,
                    object_2_id=1, object_2_content_type=self.ctype_b,
                    score=4)])

    def test_similar_to_self(self):
        """Objects can't be similar to themselves."""
        with self.assertRaises(ValidationError) as exc:
            models.ObjectSimilarity.objects.create(
                object_1_id=1, object_1_content_type=self.ctype_a,
                object_2_id=1, object_2_content_type=self.ctype_a,
                score=4)

        self.assertEqual(exc.exception.error_dict['__all__'][0].message,
                         'An object cannot be similar to itself.')

    def test_unicode(self):
        """Making pylint-django happy."""
        sim = models.ObjectSimilarity(
            object_1_id=1, object_1_content_type=self.ctype_a,
            object_2_id=2, object_2_content_type=self.ctype_b,
            score=4)

        self.assertEqual('1, 2: 4', get_unicode(sim))

    def test_default_sort(self):
        """Sorts by descending score by default."""
        sim_a = models.ObjectSimilarity.objects.create(
            object_1_id=1, object_1_content_type=self.ctype_a,
            object_2_id=2, object_2_content_type=self.ctype_b,
            score=4)
        sim_b = models.ObjectSimilarity.objects.create(
            object_1_id=1, object_1_content_type=self.ctype_a,
            object_2_id=3, object_2_content_type=self.ctype_b,
            score=6)

        self.assertEqual([sim_b, sim_a],
                         list(models.ObjectSimilarity.objects.all()))

        sim_a.score, sim_b.score = sim_b.score, sim_a.score
        sim_a.save()
        sim_b.save()

        self.assertEqual([sim_a, sim_b],
                         list(models.ObjectSimilarity.objects.all()))


class UserScoreTest(TestCase):
    """Tests for the UserRating model."""

    def setUp(self):
        self.ctype_a = ContentType.objects.create(app_label='foo')
        self.object = {'object_id': 1, 'object_content_type': self.ctype_a}

    def test_duplicate_ratings(self):
        """A user can only rate an object once."""
        user = 'foo'

        # First rating should create OK
        models.UserScore.objects.create(
            object_id=1, object_content_type=self.ctype_a,
            user=user, score=1)

        # Next one should be disallowed
        dupe_rating = models.UserScore(
            object_id=1, object_content_type=self.ctype_a,
            user=user, score=1)

        with self.assertRaises(ValidationError):
            dupe_rating.save()

        with self.assertRaises(IntegrityError):
            models.UserScore.objects.bulk_create([dupe_rating])

    def test_ratings_different_users(self):
        """Different users can rate the same object."""
        user_a = 'a'
        user_b = 'b'

        models.UserScore.objects.create(user=user_a, score=1, **self.object)
        models.UserScore.objects.create(user=user_b, score=1, **self.object)

    def test_unicode(self):
        """Making pylint-django happy."""
        user = 'foo'
        rating = models.UserScore.objects.create(
            user=user, score=3, object_id=10, object_content_type=self.ctype_a)

        self.assertEqual('foo, 10: 3.0', get_unicode(rating))
