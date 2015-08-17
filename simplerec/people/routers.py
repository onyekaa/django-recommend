# coding: utf-8
"""See README for justification. Route People to 'second' database."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import models


class DatabaseRouter(object):

    def __send_people_to_second(self, model, **hints):
        if model is models.Person:
            return 'second'
        return 'default'

    db_for_read = __send_people_to_second

    db_for_write = __send_people_to_second

    def allow_relation(self, *args, **kwargs):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        is_intended_db = ((app_label != 'people' and db == 'default') or
                          (app_label == 'people' and db == 'second'))
        return is_intended_db
