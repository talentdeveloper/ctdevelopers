"""
WSGI config for recruiter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
import site

# Assumes that the virtualenv is activated by default
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings.devt')

from django.core import wsgi
application = wsgi.get_wsgi_application()
