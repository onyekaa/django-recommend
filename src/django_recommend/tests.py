# coding: utf-8
"""Unit tests for the django_recommend app."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from . import models


class ObjectSimilarityTest(TestCase):
    """Tests for the ObjectSimilarity model."""

    def test_duplicate_similarities(self):
        """Duplicate similarities can't be created."""
        ctype_a = ContentType.objects.create(app_label='foo')
        ctype_b = ContentType.objects.create(app_label='bar')

        # Creating one should work OK
        models.ObjectSimilarity.objects.create(
            object_1_id=1, object_1_content_type=ctype_a,
            object_2_id=1, object_2_content_type=ctype_b,
            score=3)

        # Creating the second should not (even with a different score)
        with self.assertRaises(IntegrityError):
            models.ObjectSimilarity.objects.create(
                object_1_id=1, object_1_content_type=ctype_a,
                object_2_id=1, object_2_content_type=ctype_b,
                score=4)
