from django.conf import settings
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
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from braces.views import (
    JSONResponseMixin,
)
from django_countries import countries

from .models import (
    JobPost,
    Skill,
)
from .forms import (
    ConnectionInviteForm,
    JobPostForm,
    JobReferralForm,
)
from .models import (
    Connection,
    ConnectionInvite,
    ConnectionRequest,
    JobApplication,
    JobReferral,
    UserReferral,
)
from companies.models import (
    Company,
    CompanyRequestInvitation,
)
from users.mixins import (
    AgentRequiredMixin,
    CandidateRequiredMixin,
    ProfileCompleteRequiredMixin,
)
from users.models import (
    Candidate,
    CVRequest,
)

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'landing.html'


class DashboardView(ProfileCompleteRequiredMixin, TemplateView):
    template_name = 'recruit/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated and
            request.user.account_type in [User.ACCOUNT_AGENT, User.ACCOUNT_SUPPORT] and
            not request.user.profile.company):
            company = Company.objects.filter(domain=request.user.domain, owner__account_type=request.user.account_type)

            if company.exists():
                company = company.first()
                # add user to company if auto invite is activated
                if company.allow_auto_invite:
                    request.user.profile.company = company
                    request.user.profile.save()
                    return HttpResponseRedirect(reverse_lazy('companies:company_invite_success'))

                # create company request invitation and redirect to pending page
                # if auto invite is not activated
                else:
                    if not CompanyRequestInvitation.objects.filter(user=request.user).exists():
                        CompanyRequestInvitation.objects.create(
                            user=request.user,
                            company=company
                        )
                    return HttpResponseRedirect(reverse_lazy('companies:company_pending'))
            return HttpResponseRedirect(reverse_lazy('companies:company_create'))
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            return ['recruit/candidate_dashboard.html']
        elif self.request.user.account_type == User.ACCOUNT_AGENT:
            return ['recruit/agent_dashboard.html']
        elif self.request.user.account_type == User.ACCOUNT_SUPPORT:
            return ['recruit/support_dashboard.html']

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardView, self).get_context_data(*args, **kwargs)

        context['connection_requests'] = ConnectionRequest.objects.filter(connectee=self.request.user).order_by('created_at')
        context['connections'] = Connection.objects.filter(Q(connecter=self.request.user) | Q(connectee=self.request.user))

        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            context['job_referrals'] = JobReferral.objects.filter(referred_to=self.request.user.candidate)

            user_referrals = UserReferral.objects.filter(referred_to=self.request.user)
            context['candidate_referrals'] = user_referrals.filter(referred_user__account_type=User.ACCOUNT_CANDIDATE)
            context['agent_referrals'] = user_referrals.filter(referred_user__account_type=User.ACCOUNT_AGENT)
            context['cv_requests'] = CVRequest.objects\
                .filter(candidate=self.request.user.candidate)\
                .filter(status=CVRequest.STATUS_PENDING)

        return context

dashboard = DashboardView.as_view()


class SearchView(ProfileCompleteRequiredMixin, TemplateView):
    """
    View for searching job posts as candidates and searching candidates as agents.
    """
    template_name = 'recruit/search.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        search = self.request.GET.get('search', None)
        filters = self.request.GET.get('filters', None)
        results = []

        if search or filters:
            # reverse the key and value of the country dictionary
            reversed_countries = {
                value.lower(): key.lower()
                for key, value in countries
            }

            # search
            search_list = search.split()
            for item in search_list:
                country_search = reversed_countries.get(item.lower(), None)
                if country_search:
                    search_list.append(country_search)

            # filter
            filter_list = filters.split(',')
            for item in filter_list:
                country_filter = reversed_countries.get(item.lower(), None)
                if country_filter:
                    filter_list.append(country_filter)

            # generate SearchQuery item from filter
            for index, item in enumerate(filter_list):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            # generate additional SearchQuery item from search
            for index, item in enumerate(search_list):
                if not search_query:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            # job posts search
            if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
                results = JobPost.objects\
                    .annotate(search=SearchVector('title', 'skills__name', 'city', 'country'))\
                    .filter(search=search_query)\
                    .distinct('id')
            # candidate search
            elif self.request.user.account_type == User.ACCOUNT_AGENT:
                results = Candidate.objects\
                    .annotate(search=SearchVector('user__first_name', 'user__last_name', 'user__email', 'skills__name', 'city', 'country'))\
                    .filter(search=search_query)\
                    .distinct('id')

        if self.request.user.account_type == User.ACCOUNT_CANDIDATE:
            model = JobPost
            context['job_referral_form'] = JobReferralForm(initial={'candidate': self.request.user.candidate})
        elif self.request.user.account_type == User.ACCOUNT_AGENT:
            model = Candidate

        # list the cities and countries that can be filtered
        countries_search = model.objects.all().distinct('country').values_list('country', flat=True)
        cities_search = model.objects.all().distinct('city').values_list('city', flat=True)
        context['countries'] = [dict(countries).get(country) for country in countries_search if dict(countries).get(country)]
        context['cities'] = set([city.title() for city in cities_search])

        context['connection'] = Connection
        context['connection_request'] = ConnectionRequest
        context['skills'] = Skill.objects.all()

        context['results'] = results
        context['filters'] = filters.split(',') if filters else []
        context['search'] = search

        return context

search = SearchView.as_view()


class JobPostSearchView(ProfileCompleteRequiredMixin, TemplateView):
    """
    View for searching a job post.
    """
    template_name = 'recruit/job_post_search.html'

    def get_context_data(self, **kwargs):
        context = super(JobPostSearchView, self).get_context_data(**kwargs)
        context['DEBUG'] = settings.DEBUG
        return context

job_post_search = JobPostSearchView.as_view()


class JobPostListView(AgentRequiredMixin, ListView):
    """
    View for displaying the list of all the company's job posts.
    """
    model = JobPost
    context_object_name = 'job_posts'
    template_name = 'recruit/job_post_list.html'

    def get_queryset(self):
        return JobPost.objects.filter(posted_by__company=self.request.user.agent.company).order_by('-updated_at')

job_post_list = JobPostListView.as_view()


class JobPostDetailView(ProfileCompleteRequiredMixin, DetailView):
    """
    View for displaying the details of the company's job posts.
    """
    model = JobPost
    context_object_name = 'job_post'
    template_name = 'recruit/job_post_detail.html'

    def get_object(self):
        return JobPost.objects.get(uuid=self.kwargs.get('uuid'))

job_post_detail = JobPostDetailView.as_view()


class JobPostCreateView(AgentRequiredMixin, CreateView):
    """
    View for creating a new job post.
    """
    model = JobPost
    form_class = JobPostForm
    template_name = 'recruit/job_post_create_update.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_initial(self):
        return {'agent': self.request.user.agent}

job_post_create = JobPostCreateView.as_view()


class JobPostUpdateView(AgentRequiredMixin, UpdateView):
    """
    View for updating a job post.
    """
    model = JobPost
    context_object_name = 'job_post'
    form_class = JobPostForm
    template_name = 'recruit/job_post_create_update.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_object(self):
        return JobPost.objects.get(uuid=self.kwargs.get('uuid'))

job_post_update = JobPostUpdateView.as_view()


class JobPostDeleteView(AgentRequiredMixin, DeleteView):
    """
    View for deleting a job post.
    """
    model = JobPost
    context_object_name = 'job_post'
    template_name = 'recruit/job_post_delete.html'
    success_url = reverse_lazy('recruit:job_post_list')

    def get_object(self):
        return JobPost.objects.get(uuid=self.kwargs.get('uuid'))

job_post_delete = JobPostDeleteView.as_view()


class ApplicationView(CandidateRequiredMixin, ListView):
    """
    View for the My Application Page.
    """
    model = JobApplication
    context_object_name = 'job_applications'
    template_name = 'recruit/application.html'

    def get_queryset(self):
        return JobApplication.objects.filter(candidate=self.request.user.candidate)

application = ApplicationView.as_view()


class ConnectionInviteCreateView(ProfileCompleteRequiredMixin, CreateView, JSONResponseMixin):
    """
    View for inviting new users to be part of their network or team.
    """
    model = ConnectionInvite
    form_class = ConnectionInviteForm
    template_name = "recruit/connection_invite_create.html"

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        form.save()
        return self.render_json_response({
            'success': True,
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

    def get_context_data(self, *args, **kwargs):
        context = super(ConnectionInviteCreateView, self).get_context_data(*args, **kwargs)
        context['connection_invite'] = ConnectionInvite
        return context

connection_invite_create = ConnectionInviteCreateView.as_view()


class JobApplicantListView(AgentRequiredMixin, ListView):
    """
    View for showing the list of applicants in the job post.
    """
    model = JobApplication
    context_object_name = 'job_applications'
    template_name = 'recruit/job_post_applicants_list.html'

    def get_queryset(self):
        job_applications = JobApplication.objects.filter(job_post__uuid=self.kwargs.get('uuid'))
        job_applications.update(is_viewed=True)
        return job_applications

job_application_list = JobApplicantListView.as_view()
