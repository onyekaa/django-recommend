# coding: utf-8
"""Template tags for django_recommend."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.template

import django_recommend


register = django.template.Library()  # pylint: disable=invalid-name


@register.filter
def similar_objects(obj):
    """Get objects similar to obj according to ObjectSimilarity."""
    return list(django_recommend.similar_objects(obj))
