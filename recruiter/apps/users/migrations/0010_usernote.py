# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-12 16:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20170612_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('text', models.TextField(verbose_name='Text')),
                ('type', models.IntegerField(choices=[(1, 'Text'), (2, 'Call'), (3, 'Mail')], verbose_name='Type')),
                ('note_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_written', to=settings.AUTH_USER_MODEL, verbose_name='Note by')),
                ('note_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_given', to=settings.AUTH_USER_MODEL, verbose_name='Note To')),
            ],
            options={
                'verbose_name': 'User Note',
                'verbose_name_plural': 'User Notes',
            },
        ),
    ]
