import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from push_notifications.models import GCMDevice


def get_upload_path(instance, filename):
    """
    This function gets the upload path of the image.
    Returns the image path.
    """
    model = instance._meta.model_name.lower()
    return os.path.join(model, filename)


def send_email_template(subject, template, recipient, data=None):
    """
    This function sends an email using a selected template.

    Arguments:
        subject: the subject of the email
        template: the template to be used for the email
        recipient: a list of recipients the email will be sent to
        data: a dictionary to be added as context variables in the email
    """
    context = {
        'current_site': Site.objects.get_current().domain,
    }
    if data:
        context.update(data)

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.NOREPLY_EMAIL,
        recipient_list=recipient,
        fail_silently=False,
        html_message=html_content
    )

def send_push_notification(message, user):
    if message.conversation.name is not None:
        title = '{0} @ {1}'.format(message.author.get_full_name(), message.conversation.name)
    else:
        title = message.author.get_full_name()

    devices = GCMDevice.objects.filter(user=user)
    devices.send_message(
        message.text,
        title=title,
        extra={
            'sound': 'default',
            'type': 'newMessage',
            'conversation_id': message.conversation.id,
            'tag': 'chat',
        }
    )
