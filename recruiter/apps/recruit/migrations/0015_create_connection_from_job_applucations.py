from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q
from django.utils import timezone


def create_application_connections(apps, schema_editor):
    """
        Populates new relationship from old one.
    """
    Connection = apps.get_model('recruit', 'Connection')
    JobApplication = apps.get_model('recruit', 'JobApplication')

    for job_application in JobApplication.objects.all():
        connection = Connection.objects.filter(
            (Q(connecter=job_application.candidate.user) & Q(connectee=job_application.job_post.posted_by.user)) |
            (Q(connecter=job_application.job_post.posted_by.user) & Q(connectee=job_application.candidate.user))
        )
        if not connection.exists():
            Connection.objects.create(
                connecter=job_application.candidate.user,
                connectee=job_application.job_post.posted_by.user,
                connection_type=3,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0014_auto_20170608_1243'),
    ]

    operations = [
        migrations.RunPython(create_application_connections)
    ]
