# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-07 07:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20170604_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='users',
            field=models.ManyToManyField(related_name='conversations', to=settings.AUTH_USER_MODEL, verbose_name='Conversation participants'),
        ),
        migrations.AlterField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='Message author'),
        ),
        migrations.AlterField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.Conversation', verbose_name='Conversation'),
        ),
    ]
