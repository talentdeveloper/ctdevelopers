from macrosurl import url
from mail import views


urlpatterns = (
    url(r'^aliases/$', views.virtual_alias_list, name='virtual_alias_list'),
    url(r'^aliases/:pk/update/$', views.virtual_alias_update, name='aliases_update'),
    url(r'^aliases/:pk/delete/$', views.virtual_alias_delete, name='virtual_alias_delete'),
    url(r'^alerts/:pk/$', views.alert_detail, name='alert_detail'),
    url(r'^alerts/$', views.alert_list, name='alert_list'),
    url(r'^favourite/:pk/$', views.favourite_view, name='favourite'),
)
