from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin

import debug_toolbar
from django_js_reverse.views import urls_js
from macrosurl import url
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

from core.api import CoreViewSet
from recruit.api import (
    SearchViewSet,
    JobPostViewSet,
)
from users.api import (
    AccountsViewSet,
    UsersViewSet,
)

router = DefaultRouter()
router.register(r'device/fcm', GCMDeviceAuthorizedViewSet, base_name='devices')
router.register(r'', CoreViewSet, base_name='core')
router.register(r'search', SearchViewSet, base_name='search')
router.register(r'accounts', AccountsViewSet, base_name='accounts')
router.register(r'users', UsersViewSet, base_name='users')
router.register(r'jobs', JobPostViewSet, base_name='job_post')

urlpatterns = [
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('recruit.urls', namespace='recruit')),
    url(r'^companies/', include('companies.urls', namespace='companies')),
    url(r'^chat/', include('chat.urls', namespace='chat')),
    url(r'^mail/', include('mail.urls', namespace='mail')),
    url(r'^users/', include('users.urls', namespace='users')),

    url(r'^api/', include('rest_auth.urls', namespace='api-auth')),
    url(r'^api/', include(router.urls)),
    url(r'^support/', include('support.urls', namespace='support')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
