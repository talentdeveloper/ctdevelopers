from django.contrib.auth import get_user_model
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    UpdateView,
)

from braces.views import LoginRequiredMixin

from .forms import (
    AgentPhotoUploadForm,
    AgentUpdateForm,
    CandidateForm,
    CandidatePhotoUploadForm,
    CandidateUpdateForm,
    CandidateSettingsForm,
    CVRequestForm,
    SupportPhotoUploadForm,
    UserSettingsForm,
)
from .mixins import (
    CandidateRequiredMixin,
    ProfileCompleteRequiredMixin,
)
from .models import (
    Agent,
    Candidate,
    CVRequest,
    UserNote,
)
from .utils import get_profile_completeness
from chat.models import (
    Conversation,
    Message,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
    Skill,
)


User = get_user_model()


class ConfirmEmailDoneView(TemplateView):
    """
    View for showing that the user has confirmed his email
    """
    template_name = 'account/email_confirm_done.html'

email_confirm_done = ConfirmEmailDoneView.as_view()


class CandidateProfileView(LoginRequiredMixin, DetailView):
    """
    View for viewing a user's profile.
    """
    model = Candidate
    context_object_name = 'profile'
    template_name = 'users/candidate_profile.html'

    def get_object(self):
        return Candidate.objects.get(user__slug=self.kwargs.get('slug'))

    def get_context_data(self, *args, **kwargs):
        context = super(CandidateProfileView, self).get_context_data(*args, **kwargs)
        profile = self.get_object()

        is_connected = True
        if self.request.user == profile.user:
            context['profile_candidate_form'] = CandidateForm(instance=profile)
        else:
            # for requesting cv download
            if not profile.settings.auto_cv_download:
                context['cv_request_form'] = CVRequestForm()
                context['cv_request'] = CVRequest.objects\
                    .filter(requested_by=self.request.user, candidate=profile)\
                    .first()

            context['user_note'] = UserNote
            context['user_notes'] = UserNote.objects\
                .filter(note_by=self.request.user, note_to=profile.user)\
                .order_by('-created_at')

            is_connected = Connection.objects.filter(
                (Q(connecter=self.request.user) & Q(connectee=profile.user)) |
                (Q(connecter=profile.user) & Q(connectee=self.request.user))
            ).exists()
        context['is_connected'] = is_connected

        if not is_connected:
            context['connection_request'] = ConnectionRequest.objects.filter(
                (Q(connecter=self.request.user) & Q(connectee=profile.user)) |
                (Q(connecter=profile.user) & Q(connectee=self.request.user))
            ).first()

        context['skills'] = [skill.name for skill in Skill.objects.all()]
        context['photo_form'] = CandidatePhotoUploadForm
        context['completeness'] = get_profile_completeness(profile)
        context['candidate_form'] = CandidateUpdateForm(instance=profile)
        context['ConnectionRequest'] = ConnectionRequest

        if self.request.user.account_type == User.ACCOUNT_AGENT:
            messages = Message.objects\
                .filter(conversation__users=profile.user)\
                .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
                .order_by('created_at')

            sent = messages.filter(author=self.request.user)
            context['first_contact_sent'] = sent.first()

            received = messages.exclude(author=self.request.user)
            context['last_message_sent'] = sent.last()
            context['last_message_received'] = received.last()

        return context

candidate_profile = CandidateProfileView.as_view()


class CandidateSearchView(CandidateRequiredMixin, TemplateView):
    """
    View for candidates to search for another candidate to add to their network.
    """
    template_name = 'users/candidate_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CandidateSearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        candidates = []

        if search:
            search_list = search.split()

            for index, item in enumerate(search_list):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            candidates = Candidate.objects\
                .annotate(search=SearchVector('user__first_name', 'user__last_name'))\
                .filter(search=search_query)\
                .exclude(user=self.request.user)\
                .distinct('id')

        context['search'] = search
        context['candidates'] = candidates
        context['connection_request'] = ConnectionRequest

        connection_requests = ConnectionRequest.objects.filter(
            connectee__candidate__in=candidates,
            connecter=self.request.user
        )
        context['team_connection_requests'] = connection_requests\
            .filter(connection_type=ConnectionRequest.CONNECTION_TEAM)\
            .values_list('connectee__pk', flat=True)
        context['network_connection_requests'] = connection_requests\
            .filter(connection_type=ConnectionRequest.CONNECTION_NETWORK)\
            .values_list('connectee__pk', flat=True)

        return context

candidate_search = CandidateSearchView.as_view()


class AgentSearchView(ProfileCompleteRequiredMixin, TemplateView):
    """
    View for candidates to search for agents to add to their network.
    """
    template_name = "users/agent_search.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AgentSearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        agents = []

        if search:
            search_list = search.split()

            for index, item in enumerate(search_list):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            agents = Agent.objects\
                .annotate(search=SearchVector('user__first_name', 'user__last_name'))\
                .filter(search=search_query)\
                .exclude(user=self.request.user)\
                .distinct('id')

        context['search'] = search
        context['agents'] = agents
        context['connection_request'] = ConnectionRequest

        connection_requests = ConnectionRequest.objects.filter(
            connectee__agent__in=agents,
            connecter=self.request.user
        )
        context['network_connection_requests'] = connection_requests\
            .filter(connection_type=ConnectionRequest.CONNECTION_NETWORK)\
            .values_list('connectee__pk', flat=True)

        return context

agent_search = AgentSearchView.as_view()


class SettingsView(LoginRequiredMixin, UpdateView):
    """
    View for the Settings page.
    """
    model = User
    form_class = UserSettingsForm
    template_name = 'users/settings.html'
    success_url = reverse_lazy('users:settings')

    def get_object(self):
        return self.request.user

    def get_initial(self):
        user = self.request.user

        initial = {
            'user': user,
        }
        if user.account_type == user.ACCOUNT_CANDIDATE:
            initial['title'] = user.profile.title
            initial['cv'] = user.profile.settings.auto_cv_download

        return initial

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            context['settings_form'] = CandidateSettingsForm(instance=self.request.user.candidate.settings)
            context['photo_form'] = CandidatePhotoUploadForm
        elif self.request.user.account_type == User.ACCOUNT_AGENT:
            context['photo_form'] = AgentPhotoUploadForm
        elif self.request.user.account_type == User.ACCOUNT_SUPPORT:
            context['photo_form'] = SupportPhotoUploadForm

        return context

settings = SettingsView.as_view()


class CVRequestView(ProfileCompleteRequiredMixin, CreateView):
    """
    View for the CV Request.
    """
    model = CVRequest
    form_class = CVRequestForm

    def get_success_url(self):
        return reverse_lazy('users:candidate_profile', kwargs={'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def get_initial(self):
        return {
            'candidate': User.objects.get(slug=self.kwargs.get('slug')).candidate,
            'requested_by': self.request.user,
        }

cv_request = CVRequestView.as_view()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating the initial profile of the user.
    """
    model = Candidate
    form_class = CandidateForm
    template_name = 'users/candidate_update.html'
    success_url = reverse_lazy('recruit:dashboard')

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)

        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            context['photo_form'] = CandidatePhotoUploadForm
        elif self.request.user.account_type == User.ACCOUNT_AGENT:
            context['photo_form'] = AgentPhotoUploadForm
        elif self.request.user.account_type == User.ACCOUNT_SUPPORT:
            context['photo_form'] = SupportPhotoUploadForm

        return context

profile_update = ProfileUpdateView.as_view()
