# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-22 01:43
from __future__ import unicode_literals

from django.db import migrations, models


def set_username_remove_dash(apps, schema_editor):
    """
        Populates new relationship from old one.
    """
    User = apps.get_model('users', 'User')

    for user in User.objects.all():
        user.username = f'{user.first_name}{user.last_name}{user.pk}'
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20170822_0247'),
    ]

    operations = [
        migrations.RunPython(set_username_remove_dash),
    ]
