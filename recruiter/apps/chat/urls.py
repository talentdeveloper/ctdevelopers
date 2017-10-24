from macrosurl import url

from chat import views


urlpatterns = (
    url(r'^(?P<cid>\d+)?$', views.chat_view, name='chat'),
)
