from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
# from django.contrib.postgres.search import SearchVector

from django.shortcuts import render

from braces.views import LoginRequiredMixin
from .forms import (
    IssueForm,
)
from .models import (
    Issue,
)
from recruit.models import (
    Connection
)
from chat.models import (
    Conversation,
    Participant,
    Message
)
from recruit.models import (
    Connection
)
from chat.models import (
    Conversation,
    Participant,
    Message
)
from users.models import (
    Support
)
from django.views.generic import (
    # CreateView,
    # DetailView,
    # TemplateView,
    # UpdateView,
    View,
)

User = get_user_model()


class IssueCreateView(LoginRequiredMixin, View):
    """
    View for creating Support issue
    """

    template_name = 'support/issue_create_describe.html'

    def get_initial(self):
        return {'client': self.request.user}

    def get(self, request, **kwargs):
        form = []
        try:
            provider = request.session['new_issue_provider']
            provider = Support.objects.get(user__pk=provider)
        except Support.DoesNotExist:
            raise Http404('This provider is not available.')

        form = IssueForm(initial={
            'client': self.request.user,
            'provider': provider.user
        })

        return render(request, self.template_name, {
            'form': form,
            'provider': provider
        })

    def post(self, request, **kwards):
        form_values = request.POST.copy()
        form = IssueForm(form_values)

        if form.is_valid():
            new_issue = form.save(commit=True)

            # Check if the users connected
            connection = Connection.objects \
                .filter(
                    Q(connecter__in=(new_issue.client, new_issue.provider)) |
                    Q(connectee__in=(new_issue.client, new_issue.provider))
                )
            if not connection:
                Connection.objects.create(
                    connecter=new_issue.client,
                    connectee=new_issue.provider,
                    connection_type=Connection.CONNECTION_SUPPORT
                )

            # Find conversation between these two
            conversation = Conversation.objects \
                .filter(conversation_type=Conversation.CONVERSATION_USER) \
                .filter(users=new_issue.client) \
                .filter(users=new_issue.provider) \
                .first()
            if not conversation:
                conversation = Conversation.objects.create()
                Participant.objects.create(
                    user=new_issue.client,
                    conversation=conversation
                )
                Participant.objects.create(
                    user=new_issue.provider,
                    conversation=conversation
                )
                conversation.save()

            # Send message in that conversation
            Message.objects.create(
                conversation=conversation,
                author=new_issue.client,
                text="New issue: '%s'. %s" % (
                    new_issue.subject,
                    new_issue.description
                ),
            )

        return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))

issue_create_describe = IssueCreateView.as_view()


class IssueCreateSelectProviderView(LoginRequiredMixin, View):
    """
    View for creating Support issue
    """

    template_name = 'support/issue_create_select_provider.html'

    def get(self, request, *args, **kwargs):
        context = {'providers': Support.objects.all()}

        return render(request, self.template_name, context)

    def post(self, request, **kwards):
        post_values = request.POST.copy()
        request.session['new_issue_provider'] = post_values['selected_provider']
        return HttpResponseRedirect(reverse_lazy('support:issue_create_describe'))

issue_create_select_provider = IssueCreateSelectProviderView.as_view()
