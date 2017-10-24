from django.conf import settings


def global_settings(request):
    return {
        'DEBUG': settings.DEBUG
    }
