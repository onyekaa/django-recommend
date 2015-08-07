# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='content',
            field=models.CharField(unique=True, max_length=400),
        ),
        migrations.AlterUniqueTogether(
            name='favoritequote',
            unique_together=set([('user', 'quote')]),
        ),
        migrations.AlterUniqueTogether(
            name='viewedquote',
            unique_together=set([('user', 'quote')]),
        ),
    ]
