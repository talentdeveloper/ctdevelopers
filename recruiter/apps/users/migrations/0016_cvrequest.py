# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-02 15:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20170702_1206'),
    ]

    operations = [
        migrations.CreateModel(
            name='CVRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Automatic Download of CV?')),
                ('status', models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Declined')], default=0, verbose_name='Status')),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_requests', to='users.Candidate', verbose_name='Candidate')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cv_requests', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'CV Request',
                'verbose_name_plural': 'CV Requests',
            },
        ),
    ]
