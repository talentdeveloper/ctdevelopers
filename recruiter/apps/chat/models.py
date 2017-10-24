from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from core.models import AbstractTimeStampedModel, optional
from core.utils import get_upload_path


class Message(AbstractTimeStampedModel):
    """
    Model for message.
    """
    text = models.TextField(_('Message text'))
    author = models.ForeignKey(
        'users.User',
        related_name='messages',
        verbose_name=_('Message author')
    )
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )
    group_invite = models.OneToOneField(
        'chat.GroupInvite',
        on_delete=models.CASCADE,
        related_name='message',
        verbose_name=_('Invite linked to message'),
        **optional
    )

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.author.get_full_name()


class GroupInvite(AbstractTimeStampedModel):
    INVITE_ACCEPTED = 0
    INVITE_PENDING = 1
    INVITE_DECLINED = 2
    INVITE_STATUS_CHOICES = (
        (INVITE_ACCEPTED, _('Invite accepted')),
        (INVITE_PENDING, _('Invite pending')),
        (INVITE_DECLINED, _('Invite declined')),
    )

    status = models.IntegerField(
        _('Participant status'),
        choices=INVITE_STATUS_CHOICES,
        default=INVITE_PENDING,
        help_text=_('Group chat invite acceptance status.')
    )
    participant = models.ForeignKey(
        'chat.Participant',
        on_delete=models.CASCADE,
        related_name='invites',
        verbose_name=_('Participant receiving invite')
    )
    text = models.TextField(_('Invite text'))

    class Meta:
        verbose_name = _('Group invite')
        verbose_name_plural = _('Group invites')

    def __str__(self):
        return self.participant.user.get_full_name()


class Conversation(AbstractTimeStampedModel):
    """
    Model for conversation.
    """
    CONVERSATION_USER = 0
    CONVERSATION_GROUP = 1
    CONVERSATION_TYPE_CHOICES = (
        (CONVERSATION_USER, _('User chat')),
        (CONVERSATION_GROUP, _('Group chat')),
    )

    conversation_type = models.IntegerField(
        _('Conversation Type'),
        choices=CONVERSATION_TYPE_CHOICES,
        default=CONVERSATION_USER,
        help_text=_('Conversation type based on how it was created.')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Conversation name'),
        **optional
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='own_conversations',
        verbose_name=_('Conversation owner'),
        **optional
    )
    users = models.ManyToManyField(
        'users.User',
        through='chat.Participant',
        related_name='conversations',
        verbose_name=_('Conversation participants')
    )

    def clean(self):
        validations = {}

        if self.conversation_type == self.CONVERSATION_GROUP and not self.owner:
            validations['owner'] = ValidationError(
                _('Owner field should be set in group conversations'))
        if self.conversation_type == self.CONVERSATION_GROUP and not self.name:
            validations['name'] = ValidationError(
                _('Name field should be set in group conversations'))
        if self.owner not in self.users.all():
            validations['users'] = ValidationError(
                _('Owner should be present in conversation'))

        if validations:
            raise ValidationError(validations)

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')

    def __str__(self):
        return ', '.join([user.get_full_name() for user in self.users.all()])


class Participant(AbstractTimeStampedModel):
    PARTICIPANT_ACCEPTED = 0
    PARTICIPANT_PENDING = 1
    PARTICIPANT_DECLINED = 2
    PARTICIPANT_STATUS_CHOICES = (
        (PARTICIPANT_ACCEPTED, _('Participant accepted')),
        (PARTICIPANT_PENDING, _('Participant pending')),
        (PARTICIPANT_DECLINED, _('Participant declined')),
    )

    status = models.IntegerField(
        _('Participant status'),
        choices=PARTICIPANT_STATUS_CHOICES,
        default=PARTICIPANT_ACCEPTED,
        help_text=_('Participant invite acceptance status.')
    )
    last_read_message = models.ForeignKey(
        'chat.Message',
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Last read message',
        **optional
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='User'
    )
    conversation = models.ForeignKey(
        'chat.Conversation',
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Conversation'
    )

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        unique_together = [
            ['user', 'conversation']
        ]

    def __str__(self):
        return self.user.get_full_name()


class Attachment(models.Model):
    message = models.ForeignKey(
        'chat.Message',
        related_name='attachments',
        verbose_name='Message',
    )
    file = models.FileField(
        upload_to=get_upload_path,
        verbose_name='File'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='File name'
    )
    file_size = models.IntegerField(
        verbose_name='File size'
    )

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        return self.file_name
