# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-25 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170525_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='team_members',
            field=models.ManyToManyField(related_name='_candidate_team_members_+', to='users.Candidate', verbose_name='Team Members'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='networks',
            field=models.ManyToManyField(related_name='_candidate_networks_+', to='users.Candidate', verbose_name='Networks'),
        ),
    ]
