from macrosurl import url

from . import (
    api,
    views,
)


urlpatterns = (
    url(r'^create/$', views.company_create, name='company_create'),
    url(r'^update/$', views.company_update, name='company_update'),
    url(r'^pending/$', views.company_pending, name='company_pending'),
    url(r'^invite/$', views.company_invite, name='company_invite'),
    url(r'^:slug/$', views.company_detail, name='company_detail'),
    url(r'^invitation/(?P<invite_key>[0-9A-Za-z]+)/$', views.company_invite, name='company_invite'),
    url(r'^invite/success/$', views.company_invite_success, name='company_invite_success'),

    url(r'^invitation/:uuid/update/api/$', api.company_invitation_request, name='company_invitation_request'),
)
