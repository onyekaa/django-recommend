# coding: utf-8
"""Test the tests! Test that the database router is behaving as intended."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import django.db
import pytest
from django.contrib.contenttypes import models as ct_models

import people.models
import quotes.models


@pytest.mark.django_db
def test_quotes():
    """Quotes can only exist on db 'default'."""
    obj = quotes.models.Quote.objects.using('default').create(content='foo')
    assert obj.pk
    with pytest.raises(django.db.OperationalError):
        quotes.models.Quote.objects.using('second').create(content='foo')


@pytest.mark.django_db
def test_people():
    """Person objects can only exist on db 'second'."""
    obj = people.models.Person.objects.using('second').create(name='Bob')
    assert obj.pk
    with pytest.raises(django.db.OperationalError):
        people.models.Person.objects.using('default').create(name='Bob')


@pytest.mark.django_db
def test_contenttypes():
    """ContentTypes are only on db 'default'."""
    ctype = ct_models.ContentType.objects.using('default').get(model='person')
    assert ctype.pk
    assert ctype.model_class() == people.models.Person

    with pytest.raises(django.db.OperationalError):
        ct_models.ContentType.objects.using('second').get(model='person')
