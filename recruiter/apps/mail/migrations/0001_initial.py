# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-10 01:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('owner', models.IntegerField(blank=True, null=True, verbose_name='Owner')),
                ('mail_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Mail ID')),
                ('subject', models.CharField(blank=True, max_length=255, null=True, verbose_name='Subject')),
                ('message', models.TextField(verbose_name='Body')),
                ('message_date', models.DateTimeField(blank=True, null=True, verbose_name='Message Date')),
                ('size', models.IntegerField(blank=True, null=True, verbose_name='Size')),
                ('to_field', models.CharField(blank=True, max_length=255, null=True, verbose_name='To')),
                ('in_reply_to', models.CharField(blank=True, max_length=255, null=True, verbose_name='Replied to')),
                ('from_contact_email', models.CharField(blank=True, max_length=255, null=True, verbose_name='From')),
                ('favourite', models.BooleanField(default=False, verbose_name='Favourite?')),
                ('read', models.NullBooleanField(verbose_name='Read?')),
            ],
            options={
                'verbose_name': 'Email Alert',
                'verbose_name_plural': 'Email Alerts',
            },
        ),
        migrations.CreateModel(
            name='VirtualAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('domain', models.CharField(max_length=100, verbose_name='Domain')),
                ('source', models.CharField(error_messages={'unique': 'This email has already been registered.'}, max_length=100, unique=True, verbose_name='Origin')),
                ('destination', models.CharField(max_length=100, verbose_name='Destination')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('site', models.CharField(max_length=200, verbose_name='Job Site')),
                ('user_id', models.IntegerField(verbose_name='User ID')),
            ],
            options={
                'verbose_name': 'Virtual Alias',
                'verbose_name_plural': 'Virtual Aliases',
            },
        ),
        migrations.CreateModel(
            name='VirtualDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Virtual Domain',
                'verbose_name_plural': 'Virtual Domains',
            },
        ),
        migrations.CreateModel(
            name='VirtualUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(editable=False, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(editable=False, verbose_name='Updated At')),
                ('password', models.CharField(max_length=100, verbose_name='Password')),
                ('email', models.CharField(max_length=100, unique=True, verbose_name='Email')),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domain', to='mail.VirtualDomain', verbose_name='Domain')),
            ],
            options={
                'verbose_name': 'Virtual User',
                'verbose_name_plural': 'Virtual Users',
            },
        ),
    ]