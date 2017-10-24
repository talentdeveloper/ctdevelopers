from django.conf import settings
from django.views.generic import TemplateView

from users.mixins import ProfileCompleteRequiredMixin


class ChatView(ProfileCompleteRequiredMixin, TemplateView):
    template_name = 'chat/index.html'

    def get_context_data(self, **kwargs):
        context = super(ChatView, self).get_context_data(**kwargs)
        context['DEBUG'] = settings.DEBUG
        return context

chat_view = ChatView.as_view()
