# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-26 01:32
from __future__ import unicode_literals

from django.db import migrations, models



def update_connection_values(apps, schema_editor):
    """
    Update connection values to the updated format.
    """
    Connection = apps.get_model('recruit', 'Connection')
    ConnectionInvite = apps.get_model('recruit', 'ConnectionInvite')
    ConnectionRequest = apps.get_model('recruit', 'ConnectionRequest')

    for connection in Connection.objects.all():
        if connection.connection_type != 2:
            connection.connection_type == 1

    for connection_invite in ConnectionInvite.objects.all():
        if connection_invite.connection_type != 2:
            connection_invite.connection_type == 1

    for connection_request in ConnectionRequest.objects.all():
        if connection_request.connection_type != 2:
            connection_request.connection_type == 1


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0016_add_candidate_to_candidate_network_conversation'),
    ]

    operations = [
        migrations.RunPython(update_connection_values),
        migrations.AlterField(
            model_name='connection',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Network'), (2, 'Team')], verbose_name='Connection Type'),
        ),
        migrations.AlterField(
            model_name='connectioninvite',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Network'), (2, 'Team')], verbose_name='Connection Type'),
        ),
        migrations.AlterField(
            model_name='connectionrequest',
            name='connection_type',
            field=models.IntegerField(choices=[(1, 'Network'), (2, 'Team')], verbose_name='Connection Type'),
        ),
    ]
