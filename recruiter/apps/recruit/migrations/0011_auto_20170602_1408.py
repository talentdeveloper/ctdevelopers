# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-02 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0010_auto_20170531_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Candidate to Candidate Network'), (2, 'Candidate to Candidate Team Member'), (3, 'Candidate to Agent Network')], verbose_name='Connection Type'),
        ),
        migrations.AlterField(
            model_name='connectioninvite',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Candidate to Candidate Network'), (2, 'Candidate to Candidate Team Member'), (3, 'Candidate to Agent Network')], verbose_name='Connection Type'),
        ),
        migrations.AlterField(
            model_name='connectionrequest',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Candidate to Candidate Network'), (2, 'Candidate to Candidate Team Member'), (3, 'Candidate to Agent Network')], verbose_name='Connection Type'),
        ),
    ]
