# coding: utf-8
"""Allow pyrecommend to write to the Django database."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import models


class ResultStorage(object):  # pylint: disable=too-few-public-methods
    """Write items to the Django database."""

    def __setitem__(self, key, val):
        models.ObjectSimilarity.set(*key, score=val)
