# coding: utf-8
"""Tasks for recommendations."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import threading
import time

import pyrecommend.similarity
from django.contrib.contenttypes import models as ct_models

from . import storage
from .conf import settings


LOG = logging.getLogger(__name__)


THREADED = False


# Support Celery if it's available
try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        """Add a mock 'delay' method."""

        def delay(*args):  # pragma: no cover
            """For debugging; update suggestions in background thread."""
            if not THREADED:
                return update_similarity(*args)

            def delayed(all_args):
                """Run similarity calculations."""
                time.sleep(1)  # Give SQLite DB time to finish transactions.
                update_similarity(all_args)

            proc = threading.Thread(target=delayed, args=args)
            proc.start()

        func.delay = delay
        return func


def signal_handler(**kwargs):
    """Kickoff the update similarity calculation below.

    This will figure out what asynchronous method is most appropriate to use.
    (E.g. celery, or if debugging Python threads, etc.)

    """
    if not settings.RECOMMEND_ENABLE_AUTOCALC:
        return
    user_score = kwargs['instance']
    content_type_id = user_score.object_content_type_id
    object_id = user_score.object_id
    params = object_id, content_type_id
    update_similarity.delay(params)


@shared_task
def update_similarity(obj_params):
    """Update similarity scores for object and all related objects.

    obj_params:
        A tuple of (object_id, object_content_type_id).
        May also be a single model instance, instead.

    """
    LOG.info('Calculating simlarity for %s', obj_params)
    try:
        obj_id, ctype_id = obj_params
    except TypeError:  # Not iterable, must be a Django obj
        obj = obj_params
    else:
        content_type = ct_models.ContentType.objects.get(pk=ctype_id)
        obj = content_type.model_class().objects.get(pk=obj_id)

    obj_data = storage.ObjectData(obj)
    sim_func = pyrecommend.similarity.dot_product
    pyrecommend.calculate_similarity(
        obj_data, sim_func, storage.ResultStorage())
