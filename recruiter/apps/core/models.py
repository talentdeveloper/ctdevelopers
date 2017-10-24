from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


optional = {
    'blank': True,
    'null': True,
}


class AbstractTimeStampedModel(models.Model):
    """
    Base for time-stamped models.
    """

    created_at = models.DateTimeField(_('Created At'), editable=False)
    updated_at = models.DateTimeField(_('Updated At'), editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # check if the instace already has an id
        if not self.created_at:
            self.created_at = timezone.now()

        # update date modified
        self.updated_at = timezone.now()

        return super(AbstractTimeStampedModel, self).save(*args, **kwargs)
