# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-26 16:43
from __future__ import unicode_literals

import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0013_auto_20170724_0934'),
        ('users', '0018_userlocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, verbose_name='Phone')),
                ('photo', models.ImageField(blank=True, help_text='200x200px', null=True, upload_to=core.utils.get_upload_path, verbose_name='Photo')),
                ('status', models.IntegerField(choices=[(0, 'Active'), (1, 'Inactive'), (2, 'Moderation')], default=0, verbose_name='Status')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supports', to='companies.Company', verbose_name='Company')),
            ],
            options={
                'verbose_name': 'Support',
                'verbose_name_plural': 'Supports',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.IntegerField(choices=[(1, 'Candidate'), (2, 'Agent'), (3, 'Support')], default=1, help_text='User role selected during registration', verbose_name='Account Type'),
        ),
        migrations.AddField(
            model_name='support',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='support', to=settings.AUTH_USER_MODEL),
        ),
    ]
