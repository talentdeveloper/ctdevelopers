# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-23 04:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0010_remove_company_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='owner',
        ),
    ]