from .common import *


DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recruiter',
        'USER': 'recruiter',
        'PASSWORD': 'recruiter!',
        'HOST': 'postgres',
        'PORT': '',
    },
    'mailserver': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mail_dev',
        'USER': 'mail',
        'PASSWORD': 'pass&1413',
        'HOST': '109.74.206.34',
        'PORT': '',
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Django-channels settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis/0", 6379)],
        },
        "ROUTING": "conf.routing.channel_routing",
    },
}


####################################################################################################
# Logging Configurations
####################################################################################################

ADMINS = (
    ('Lorence Lim', 'jlorencelim@gmail.com'),
)
MANAGERS = ADMINS + ('Matt Codina', 'mattcodina.work@gmail.com')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d] %(message)s'
        },
        'normal': {
            'format': '[%(levelname)s %(asctime)s %(module)s] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s %(asctime)s] %(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'debug_log_file': {
            'formatter': 'normal',
            'level': 'DEBUG',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'W0',
            'encoding': 'utf-8'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        'debug_log': {
            'handlers': ['debug_log_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


try:
    from .local import *
except ImportError:
    pass
