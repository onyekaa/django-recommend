# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0003_auto_20150803_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousViewedQuote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_key', models.CharField(max_length=255)),
                ('quote', models.ForeignKey(to='quotes.Quote')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='anonymousviewedquote',
            unique_together=set([('session_key', 'quote')]),
        ),
    ]
