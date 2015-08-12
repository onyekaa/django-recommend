# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_auto_20150806_1839'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='anonymousviewedquote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='anonymousviewedquote',
            name='quote',
        ),
        migrations.AlterUniqueTogether(
            name='favoritequote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='favoritequote',
            name='quote',
        ),
        migrations.RemoveField(
            model_name='favoritequote',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='quotesimilarity',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='quotesimilarity',
            name='quote_1',
        ),
        migrations.RemoveField(
            model_name='quotesimilarity',
            name='quote_2',
        ),
        migrations.AlterUniqueTogether(
            name='viewedquote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='viewedquote',
            name='quote',
        ),
        migrations.RemoveField(
            model_name='viewedquote',
            name='user',
        ),
        migrations.DeleteModel(
            name='AnonymousViewedQuote',
        ),
        migrations.DeleteModel(
            name='FavoriteQuote',
        ),
        migrations.DeleteModel(
            name='QuoteSimilarity',
        ),
        migrations.DeleteModel(
            name='ViewedQuote',
        ),
    ]
