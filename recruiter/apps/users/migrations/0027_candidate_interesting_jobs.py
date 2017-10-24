# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-01 13:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0019_jobinterest'),
        ('users', '0026_auto_20170908_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='interesting_jobs',
            field=models.ManyToManyField(related_name='_candidate_interesting_jobs_+', through='recruit.JobInterest', to='recruit.JobPost', verbose_name='Job Interests'),
        ),
    ]