# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-08 18:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_username_remove_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='title',
            field=models.CharField(default=1, max_length=200, verbose_name='Job title'),
            preserve_default=False,
        ),
    ]
