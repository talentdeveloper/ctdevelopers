"""
Django settings for recruiter project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from django.utils.translation import ugettext_lazy as _

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
APP_DIR = os.path.join(BASE_DIR, 'apps')
LOG_DIR = os.path.join(BASE_DIR, 'var', 'logs')

# App/Library Paths
sys.path.append(APP_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')no_g$60popv3=ki4$omo2kx0++kx)a2*lot@41+2xyup*-&p%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.104',
    '192.168.1.100',
    '192.168.1.102',
    '192.168.1.105',
    '192.168.0.108',
    '192.168.0.100',
]

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'django.contrib.postgres',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'bootstrapform',
    'channels',
    'django_extensions',
    'django_js_reverse',
    'easy_thumbnails',
    'el_pagination',
    'jsonify',
    'phonenumber_field',
    'push_notifications',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'webpack_loader',
    'widget_tweaks',

    'chat',
    'companies',
    'core',
    'mail',
    'recruit',
    'users',
    'support'
)

MIDDLEWARE = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',

    'chat.middleware.ActiveUserMiddleware'
)

ROOT_URLCONF = 'conf.urls'
WSGI_APPLICATION = 'conf.wsgi.prod.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASE_ROUTERS = ['mail.router.MailRouter',]

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


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

# TRANSMETA language configuration
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _('English')),
)

LANGUAGE_COOKIE_NAME = 'lang'

LANGUAGE_SESSION_KEY = 'lang'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


####################################################################################################
# Frontend-related configuration
####################################################################################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                #"django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.request', ## For EL-pagination
                'core.context_processors.global_settings'
            ],
            #'loaders':[
            #    'django.template.loaders.filesystem.Loader',
            #    'django.template.loaders.app_directories.Loader'
            #],
            'debug': DEBUG,
        },
    },
]

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'frontend', 'static.prod')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'static'),
    os.path.join(BASE_DIR, 'frontend', 'assets')
)

# Webpack loader settings

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'dist/', # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}

# GeoIP Patch
GEOIP_PATH = os.path.join(BASE_DIR, 'apps/core/geoip')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'frontend', 'media')

THUMBNAIL_ALIASES = {
}

# imagine: use temporary images or upload directly
IMAGINE_USE_TEMP = False
TEMP_UPLOAD_DIR = MEDIA_ROOT + 'upload/'


####################################################################################################
# Authentication
####################################################################################################

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
        'users.auth.CustomAuth',
        # Needed to login by username in Django admin, regardless of `allauth`
        "django.contrib.auth.backends.ModelBackend",
        # `allauth` specific authentication methods, such as login by e-mail
        "allauth.account.auth_backends.AuthenticationBackend",
)

# sessions (optional)
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db" # it's not a default
SESSION_CACHE_ALIAS = "default"

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# cache (optional)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'recruiter-cache',
    }
}

USER_ONLINE_TIMEOUT = 120

# Django-channels settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "conf.routing.channel_routing",
    },
}


# Start allauth settings
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_SIGNUP_FORM_CLASS = 'users.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True  # don't ask on sign out
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_ADAPTER = 'users.account_adapter.CustomAccountAdapter'
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'squareballoon', 'root']
ACCOUNT_USERNAME_VALIDATORS = None
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/users/email/confirmed/'
ACCOUNT_EMAIL_VERIFICATION_SENT_WITH_USER = True

# social providers

# SOCIALACCOUNT_PROVIDERS = \
#     {'facebook':
#         {'METHOD': 'oauth2',
#          'SCOPE': ['email', 'public_profile', 'user_friends'],
#          'AUTH_PARAMS': {'auth_type': 'https'},
#          'FIELDS': [
#              'id',
#              'email',
#              'name',
#              'first_name',
#              'last_name',
#              'verified',
#              'locale',
#              'timezone',
#              'link',
#              'gender',
#              'updated_time'],
#          'EXCHANGE_TOKEN': True,
#          'VERIFIED_EMAIL': True,
#          'VERSION': 'v2.4'}}


####################################################################################################
# Integrations Behaviour Configurations
####################################################################################################

# google reCAPTCHA 2 settings
RECAPTCHA_PUBLIC_KEY = 'pub_key'
RECAPTCHA_PRIVATE_KEY = 'priv_key'
# NOCAPTCHA = False   nouse
# RECAPTCHA_USE_SSL = True  nouse
# CAPTCHA_AJAX = False  nouse
#RECAPTCHA_PROXY = 'http://192.168.0.102:9000'

PHONENUMBER_DB_FORMAT = 'E164'
SEO_MODELS = True

# Django JS Reverse Configurations
JS_REVERSE_JS_MINIFY = False


####################################################################################################
# Email Configurations
####################################################################################################

EMAIL_PROJECT_NAME = 'squareballoon'
NOREPLY_EMAIL = 'noreply@mail2.squareballoon.com'
DEFAULT_SUPPORT_EMAIL = 'support@mail2.squareballoon.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@mail2.squareballoon.com'
EMAIL_HOST_PASSWORD = 'b1cdca6177c53f9bba4e9538e3eac5f8'
SERVER_EMAIL = "noreply@mail2.squareballoon.com"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = SERVER_EMAIL


####################################################################################################
# Logging Configurations
####################################################################################################

# ADMINS = (
#     ('Lorence', 'jlorencelim@gmail.com'),
# )

# MANAGERS = ADMINS

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

REST_AUTH_SERIALIZERS = {
    'PASSWORD_RESET_SERIALIZER': 'users.serializers.PasswordSerializer',
}
OLD_PASSWORD_FIELD_ENABLED = True


PUSH_NOTIFICATIONS_SETTINGS = {
    'FCM_API_KEY': 'AAAAqKYYf4E:APA91bH1_7Se6BBZuqX0C5xwYh5-9dw847Jr3EKlalmHyKqVaJk4HinclYrx8IMmt4mRbGvWv2uGwoQKi42SyVNYeLGyrMx7EuIHLFYJb6Dq9DjBncxEYidWUAP8H-0AHucT_wBs3SvF',
    'FCM_ERROR_TIMEOUT': 1000,
    'UPDATE_ON_DUPLICATE_REG_ID': True,
}
