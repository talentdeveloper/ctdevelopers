# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-27 01:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20170726_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlocation',
            name='ip_addr',
        ),
        migrations.AddField(
            model_name='userlocation',
            name='ip_address',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='IP Address'),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='continent_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Continent Code'),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='country_code',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Country Code'),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='country_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Country Name'),
        ),
    ]
