from django.db.models import Q
from django.template import Library

from recruit.models import (
    Connection,
    ConnectionRequest,
)


register = Library()


@register.filter
def connections(connecter, connectee):
    return Connection.objects.filter(
        (Q(connecter=connecter) & Q(connectee=connectee)) |
        (Q(connecter=connectee) & Q(connectee=connecter))
    ).first()


@register.filter
def connection_requests(user, connection_type):
    return user.connectee_requests\
        .filter(connection_type=connection_type)\
        .values_list('connectee__pk', flat=True)


@register.filter
def has_connection(connecter, connectee):
    return Connection.objects.filter(
        (Q(connecter=connecter) & Q(connectee=connectee)) |
        (Q(connecter=connectee) & Q(connectee=connecter))
    ).exists()


@register.filter
def has_connection_request(connecter, connectee):
    return ConnectionRequest.objects.filter(
        (Q(connecter=connecter) & Q(connectee=connectee)) |
        (Q(connecter=connectee) & Q(connectee=connecter))
    ).exists()
