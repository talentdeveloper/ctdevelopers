from macrosurl import url

from . import (
    api,
    views,
)


urlpatterns = (
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^dashboard/applications/$', views.application, name='application'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^search/jobs/$', views.job_post_search, name='job_post_search'),
    url(r'^job-posts/$', views.job_post_list, name='job_post_list'),
    url(r'^job-posts/:uuid/$', views.job_post_detail, name='job_post_detail'),
    url(r'^job-posts/create/$', views.job_post_create, name='job_post_create'),
    url(r'^job-posts/:uuid/update/$', views.job_post_update, name='job_post_update'),
    url(r'^job-posts/:uuid/delete/$', views.job_post_delete, name='job_post_delete'),
    url(r'^connection/invite/$', views.connection_invite_create, name='connection_invite_create'),
    url(r'^job-posts/:uuid/applicants/$', views.job_application_list, name='job_application_list'),

    url(r'^connection/request/create/api/$', api.connection_request_create, name='connection_request_create'),
    url(r'^connection/request/:uuid/delete/api/$', api.connection_request_delete, name='connection_request_delete'),
    url(r'^job-referral/create/api/$', api.job_referral_create, name='job_referral_create'),
    url(r'^user-referral/create/api/$', api.user_referral_create, name='user_referral_create'),
    url(r'^job/:uuid/application/api/$', api.job_application, name='job_application'),
)
