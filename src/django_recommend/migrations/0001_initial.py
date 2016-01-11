# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectSimilarity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_1_id', models.IntegerField()),
                ('object_2_id', models.IntegerField()),
                ('score', models.FloatField()),
                ('object_1_content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
                ('object_2_content_type', models.ForeignKey(related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-score'],
            },
        ),
        migrations.CreateModel(
            name='UserScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField()),
                ('user', models.CharField(max_length=255, db_index=True)),
                ('score', models.FloatField()),
                ('object_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userscore',
            unique_together=set([('object_id', 'object_content_type', 'user')]),
        ),
        migrations.AlterIndexTogether(
            name='userscore',
            index_together=set([('object_id', 'object_content_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='objectsimilarity',
            unique_together=set([('object_1_id', 'object_1_content_type', 'object_2_id', 'object_2_content_type')]),
        ),
        migrations.AlterIndexTogether(
            name='objectsimilarity',
            index_together=set([('object_1_id', 'object_1_content_type'), ('object_2_id', 'object_2_content_type')]),
        ),
    ]
