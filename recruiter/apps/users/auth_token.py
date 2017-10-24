import functools

from channels.handler import AsgiRequest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
authenticators = [auth() for auth in api_settings.DEFAULT_AUTHENTICATION_CLASSES]


def rest_token_user(func):
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        try:
            # We want to parse the WebSocket (or similar HTTP-lite) message
            # to get cookies and GET, but we need to add in a few things that
            # might not have been there.
            if 'method' not in message.content:
                message.content['method'] = 'FAKE'
            request = AsgiRequest(message)

        except Exception as e:
            raise ValueError('Cannot parse HTTP message - are you sure this is a HTTP consumer? {}'.format(e))

        user = None
        auth = None
        auth_token = request.GET.get('token', None)

        if auth_token:
            # comptatibility with rest framework
            request._request = {}
            request.META['HTTP_AUTHORIZATION'] = 'token {}'.format(auth_token)
            for authenticator in authenticators:
                try:
                    user_auth_tuple = authenticator.authenticate(request)
                except AuthenticationFailed:
                    pass

                if user_auth_tuple:
                    message._authenticator = authenticator
                    user, auth = user_auth_tuple
                    break

        if user is not None:
            message.user = user
            message.channel_session['user_id'] = message.user.id
        elif message.channel_session is not None and 'user_id' in message.channel_session:
            message.user = get_user_model().objects.get(id=int(message.channel_session['user_id']))

        # Run the consumer
        result = func(message, *args, **kwargs)
        return result

    return inner
