# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 13:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0013_auto_20170623_1003'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='event',
            new_name='group_invite',
        ),
    ]