# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0002_auto_20150729_1742'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteSimilarity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField()),
                ('quote_1', models.ForeignKey(related_name='+', to='quotes.Quote')),
                ('quote_2', models.ForeignKey(related_name='+', to='quotes.Quote')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quotesimilarity',
            unique_together=set([('quote_1', 'quote_2')]),
        ),
    ]
