from macrosurl import url

from . import (
    api,
    views,
)

urlpatterns = (
    url(r'^issue/create/step1-select-provider/$', views.issue_create_select_provider, name='issue_create_select_provider'),
    url(r'^issue/create/step2-describe/$', views.issue_create_describe, name='issue_create_describe'),
    url(r'^issue/:uuid/api/$', api.issue_tracking, name='issue_tracking_api'),
    url(r'^issue/conversation/:pk/api/$', api.issues_for_conversation, name='issue_for_conversation_api'),
    url(r'^issue/:uuid/close/api/$', api.issue_close, name='issue_close_api'),
)
