# coding: utf-8
"""Unit tests for the django_recommend app."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from . import models


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

        self.assertEqual("1, 2: 4", unicode(sim))
