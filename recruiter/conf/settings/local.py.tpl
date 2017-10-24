DEBUG = True

AUTH_PASSWORD_VALIDATORS = []

ACCOUNT_EMAIL_VERIFICATION = 'none'

# Webpack dev server url
STATIC_URL = 'http://localhost:3000/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recruiter',
        'USER': 'recruiter',
        'PASSWORD': 'recruiter!',
        'HOST': '',
        'PORT': '',
    },
    'mailserver': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mail',
        'USER': 'mail',
        'PASSWORD': 'pass&1413',
        'HOST': '',
        'PORT': '',
    },
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'recruiter-cache',
    }
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "conf.routing.channel_routing",
    },
}
