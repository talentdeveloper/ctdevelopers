from __future__ import unicode_literals

from django.db import migrations
from django.utils import timezone


def add_candidate_to_candidate_network_conversation(apps, schema_editor):
    """
    Create conversations for users who doesn't have even though they are connected.
    """
    Connection = apps.get_model('recruit', 'Connection')
    Conversation = apps.get_model('chat', 'Conversation')
    Participant = apps.get_model('chat', 'Participant')

    for connection in Connection.objects.all():
        conversation = Conversation.objects \
            .filter(conversation_type=0) \
            .filter(users=connection.connecter) \
            .filter(users=connection.connectee)

        if not conversation.exists():
            conversation = Conversation.objects.create()
            Participant.objects.bulk_create([
                Participant(
                    user=connection.connecter,
                    conversation=conversation,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                ),
                Participant(
                    user=connection.connectee,
                    conversation=conversation,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                ),
            ])


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0015_create_connection_from_job_applucations'),
    ]

    operations = [
        migrations.RunPython(add_candidate_to_candidate_network_conversation)
    ]
