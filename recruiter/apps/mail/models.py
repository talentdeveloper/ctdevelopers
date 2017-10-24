from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import (
    AbstractTimeStampedModel,
    optional,
)


User = get_user_model()


class EmailAlert(AbstractTimeStampedModel):
    owner = models.IntegerField(_('Owner'), **optional)
    mail_id = models.CharField(_('Mail ID'), max_length=255, **optional)
    subject = models.CharField(_('Subject'), max_length=255, **optional)
    message = models.TextField(_('Body'))
    message_date = models.DateTimeField('Message Date', **optional)
    size = models.IntegerField(_('Size'), **optional)
    to_field = models.CharField(_('To'), max_length=255, **optional)
    in_reply_to = models.CharField(('Replied to'), max_length=255, **optional)
    from_contact_email = models.CharField(_('From'), max_length=255, **optional)
    favourite = models.BooleanField(_('Favourite?'), default=False)
    read = models.NullBooleanField(_('Read?'), **optional)

    class Meta:
        verbose_name = _('Email Alert')
        verbose_name_plural = _('Email Alerts')

    def __str__(self):
        return self.to_field


class VirtualAlias(AbstractTimeStampedModel):
    domain = models.CharField(_('Domain'), max_length=100)
    source = models.CharField(
        _('Origin'),
        max_length=100,
        unique=True,
        error_messages={'unique':'This email has already been registered.'}
    )
    destination = models.CharField(_('Destination'), max_length=100)
    name = models.CharField(_('Name'), max_length=100)
    site = models.CharField(_('Job Site'), max_length=200)
    user_id = models.IntegerField(_('User ID'))

    class Meta:
        verbose_name = _('Virtual Alias')
        verbose_name_plural = _('Virtual Aliases')

    def __str__(self):
        return self.source


class VirtualDomain(AbstractTimeStampedModel):
    name = models.CharField(_('Name'), max_length=50)

    class Meta:
        verbose_name = _('Virtual Domain')
        verbose_name_plural = _('Virtual Domains')

    def __str__(self):
        return self.name


class VirtualUser(AbstractTimeStampedModel):
    domain = models.ForeignKey('mail.VirtualDomain', related_name='domain', verbose_name=_('Domain'))
    password = models.CharField(_('Password'), max_length=100)
    email = models.CharField(_('Email'), max_length=100, unique=True)

    class Meta:
        verbose_name = _('Virtual User')
        verbose_name_plural = _('Virtual Users')

    def __str__(self):
        return self.email
