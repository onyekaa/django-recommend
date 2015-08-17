# coding: utf-8
"""People models."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.db import models


class Person(models.Model):
    """Simple model to existing on a different DB than the rest of the app."""
    name = models.CharField(max_length=255)
