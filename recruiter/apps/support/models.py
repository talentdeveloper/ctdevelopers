from django.db import models
from django.db.models import Q

import uuid
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from core.models import AbstractTimeStampedModel #, optional

User = get_user_model()


class Issue(AbstractTimeStampedModel):
    """
    Model for Issue.
    """

    STATUS_OPEN = 0
    STATUS_WAIT_CLIENT = 1
    STATUS_WAIT_PROVIDER = 2
    STATUS_CLOSE = 3
    STATUS_CHOICES = (
        (STATUS_OPEN, _('Open')),
        (STATUS_WAIT_CLIENT, _('Waiting Client')),
        (STATUS_WAIT_PROVIDER, _('Waiting Provider')),
        (STATUS_CLOSE, _('Closed')),
    )
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_OPEN)

    subject = models.CharField(
        verbose_name=_('Issue Subject'),
        max_length=200,
        help_text='Short description of your issue, like "server in the room #215 is down".'
    )
    description = models.TextField(_('Problem Description'))

    uuid = models.UUIDField(_('Issue unique id'), default=uuid.uuid4, editable=False)
    client = models.ForeignKey('users.User', related_name='+', verbose_name=_('Client'))
    provider = models.ForeignKey('users.User', related_name='+', verbose_name=_('Provider'))

    class Meta:
        verbose_name = _('IT Support Issue')
        verbose_name_plural = _('IT Support Issues')

    def __str__(self):
        return str(self.uuid)

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'client': self.client.pk,
            'provider': self.provider.pk,
            'subject': self.subject,
            'description': self.description,
            'status': self.status,
            'status_humanreadable': self.get_status_display(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def change_status_to(self, target_state):
        """ Change state and log it """
        self.status = target_state
        IssueStateChange.objects.create(
            from_state=self.status,
            to_state=target_state,
            issue=self,
        )
        self.save()

    def seconds_left(self):
        tzinfo = self.updated_at.tzinfo
        response_deadline = self.updated_at + timedelta(minutes=15)
        time_left = response_deadline - datetime.now().replace(tzinfo=tzinfo)
        return time_left.total_seconds()

    @classmethod
    def change_state_based_on_new_message(cls, from_user, conversation, message):
        """ Find an issue corresponding to a message and update its status

        if the message from provider to a client, set STATUS_WAIT_CLIENT
        if the message from client to a provider, set STATUS_WAIT_PROVIDER

        returns number of affected issues (integer). Currently 1 or 0

        """
        q = ~Q(status=cls.STATUS_CLOSE)
        q &= (Q(provider=from_user) | Q(client=from_user))
        qs = cls.objects.filter(q)
        if not qs.exists():
            return 0

        # TODO: multiple cases?
        other_user = conversation.users.filter(~Q(pk=from_user.pk))
        lookup_from_provider = (Q(provider=from_user) & Q(client=other_user))
        lookup_from_client = (Q(provider=other_user) & Q(client=from_user))

        issue = qs.filter(lookup_from_provider)
        if issue.exists():
            issue = issue.first()
            # provider responds, waiting reply from client
            issue.change_status_to(cls.STATUS_WAIT_CLIENT)
            return 1

        issue = qs.filter(lookup_from_client)
        if issue.exists():
            issue = issue.first()
            # client responds, waiting reply from provider
            issue.change_status_to(cls.STATUS_WAIT_PROVIDER)
            return 1


class IssueStateChange(AbstractTimeStampedModel):
    from_state = models.IntegerField(
        _('Initial state'),
        choices=Issue.STATUS_CHOICES,
        default=Issue.STATUS_OPEN
    )
    to_state = models.IntegerField(
        _('Final state'),
        choices=Issue.STATUS_CHOICES,
        default=Issue.STATUS_CLOSE
    )
    issue = models.ForeignKey('support.Issue', verbose_name=('Referred Issue'))
