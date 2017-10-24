from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    View,
)

from braces.views import LoginRequiredMixin

from .forms import (
    CompanyForm,
    CompanyInvitationForm,
    CompanyUpdateForm,
)
from .models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
)
from chat.models import (
    Conversation,
    Message,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
)
from users.forms import AgentPhotoUploadForm
from users.mixins import (
    AgentSupportRequiredMixin,
)
from users.models import (
    Agent,
    Support,
    UserNote,
)


User = get_user_model()


class CompanyUpdateView(AgentSupportRequiredMixin, View):
    """
    View for updating the company.
    """
    template_name = 'companies/company_update.html'

    def get(self, request, **kwargs):
        form = []
        try:
            company = Company.objects.get(owner=request.user)
        except Company.DoesNotExist:
            raise Http404('You have no rights to edit company details.')

        form = CompanyUpdateForm(instance=company)

        return render(request, self.template_name, {
            'form': form,
            'company': company
        })

    def post(self, request, **kwards):
        form = []
        company = []
        form_values = request.POST.copy()

        try:
            company = Company.objects.get(owner=request.user)
            form_values['owner'] = company.owner
        except Company.DoesNotExist:
            raise Http404('You have no rights to edit company details.')

        form = CompanyUpdateForm(form_values, request.FILES, instance=company)

        if form.is_valid():
            company = form.save(commit=True)

        return render(request, self.template_name, {
            'form': form,
            'company': company
        })

company_update = CompanyUpdateView.as_view()


class CompanyInviteView(AgentSupportRequiredMixin, CreateView):
    """
    View for inviting user to the company.
    """
    model = CompanyInvitation
    form_class = CompanyInvitationForm
    template_name = 'companies/company_invite.html'

    def get_initial(self):
        return {'inviter': self.request.user}

    def get_success_url(self):
        return reverse_lazy('companies:company_detail', kwargs={'slug': self.request.user.profile.company.slug})

company_invite = CompanyInviteView.as_view()


class CompanyCreateView(AgentSupportRequiredMixin, CreateView):
    """
    View for creating a company for a new user.
    """
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_create.html'

    def get_success_url(self):
        return reverse_lazy('recruit:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
            request.user.account_type in [User.ACCOUNT_AGENT, User.ACCOUNT_SUPPORT] and
            request.user.profile.company):
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyCreateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'user': self.request.user}

company_create = CompanyCreateView.as_view()


class CompanyPendingView(AgentSupportRequiredMixin, TemplateView):
    """
    View for requesting an invitation to a company.
    """
    template_name = 'companies/company_pending.html'

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
            request.user.account_type in [User.ACCOUNT_AGENT, User.ACCOUNT_SUPPORT] and
            request.user.profile.company):
            return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(CompanyPendingView, self).dispatch(request, *args, **kwargs)

company_pending = CompanyPendingView.as_view()


class CompanyInviteSuccessView(AgentSupportRequiredMixin, DetailView):
    """
    View for the success page when successfully invited to a company.
    """
    model = Company
    template_name = 'companies/company_invite_success.html'

    def get_object(self):
        return self.request.user.profile.company

company_invite_success = CompanyInviteSuccessView.as_view()


class CompanyDetailView(LoginRequiredMixin, DetailView):
    """
    View for the Company's profile.
    """
    model = Company
    template_name = 'companies/company_detail.html'

    def get_object(self):
        return Company.objects.get(slug=self.kwargs.get('slug'))

    def get_context_data(self, *args, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(*args, **kwargs)

        company = self.get_object()
        if company.company_type == company.COMPANY_RECRUITMENT:
            profile = Agent.objects.filter(pk=self.request.GET.get('profile'))
        elif company.company_type == company.COMPANY_SUPPORT:
            profile = Support.objects.filter(pk=self.request.GET.get('profile'))
        current_profile = profile.first() if profile.exists() else company.owner.profile

        context['photo_form'] = AgentPhotoUploadForm
        context['invitation_requests'] = CompanyRequestInvitation.objects.filter(company=company)
        context['current_profile'] = current_profile

        context['user_note'] = UserNote
        context['user_notes'] = UserNote.objects\
            .filter(note_by=self.request.user, note_to=current_profile.user)\
            .order_by('-created_at')

        context['current_profile_connection'] = Connection.objects.filter(
            (Q(connectee=self.request.user) & Q(connecter=current_profile.user)) |
            (Q(connectee=current_profile.user) & Q(connecter=self.request.user))
        ).first()
        context['connection_request'] = ConnectionRequest
        context['current_profile_connection_request'] = ConnectionRequest.objects.filter(
            (Q(connectee=self.request.user) & Q(connecter=current_profile.user)) |
            (Q(connectee=current_profile.user) & Q(connecter=self.request.user))
        ).first()

        messages = Message.objects\
            .filter(conversation__users=current_profile.user)\
            .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
            .order_by('created_at')

        sent = messages.filter(author=self.request.user)
        context['first_contact_sent'] = sent.first()

        received = messages.exclude(author=self.request.user)
        context['last_message_sent'] = sent.last()
        context['last_message_received'] = received.last()

        company_users = [company_profile.user for company_profile in company.agents.all()]
        if self.request.user not in company_users:
            last_message = Message.objects\
                .filter(conversation__users__in=company_users)\
                .filter(conversation__users=self.request.user)\
                .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
                .order_by('created_at')\
                .last()
            context['last_person_in_contact'] = last_message.conversation.participants.exclude(user=self.request.user).first() if last_message else None

            last_user_note = UserNote.objects\
                .filter(note_by=self.request.user)\
                .filter(note_to__in=company_users)\
                .last()
            context['last_person_added_manual_track'] = last_user_note.note_to if last_user_note else None

        return context

company_detail = CompanyDetailView.as_view()
