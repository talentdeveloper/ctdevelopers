from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
)

from braces.views import LoginRequiredMixin, JSONResponseMixin
from django_countries import countries
from rest_framework import (
    filters,
    viewsets,
)
from rest_framework.decorators import (
    detail_route,
    list_route,
)
from rest_framework.response import Response

from .forms import (
    ConnectionRequestForm,
    JobApplicationForm,
    JobReferralForm,
    UserReferralForm,
)
from .models import (
    Connection,
    ConnectionRequest,
    JobApplication,
    JobInterest,
    JobPost,
    JobReferral,
    UserReferral,
)
from .serializers import (
    JobApplicationSerializer,
    JobInterestSerializer,
    JobPostSerializer,
    JobReferralSerializer,
)
from core.serializers import LocationSerializer
from users.mixins import CandidateRequiredMixin


class ConnectionRequestCreateAPIView(LoginRequiredMixin, CreateView, JSONResponseMixin):
    """
    API view for requesting a connection to another candnidate.
    """
    model = ConnectionRequest
    form_class = ConnectionRequestForm

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

connection_request_create = ConnectionRequestCreateAPIView.as_view()


class ConnectionRequestDeleteAPIView(LoginRequiredMixin, DeleteView, JSONResponseMixin):
    """
    API View for accepting or declining a connection request.
    """
    model = ConnectionRequest

    def get_object(self):
        return ConnectionRequest.objects.get(uuid=self.kwargs.get('uuid'))

    def post(self, request, *args, **kwargs):
        connection_request = self.get_object()
        connection_request.delete()

        if request.POST.get('action') == 'accept':
            Connection.objects.create(
                connecter=connection_request.connecter,
                connectee=connection_request.connectee,
                connection_type=connection_request.connection_type,
            )

        return self.render_json_response({'success': True})

connection_request_delete = ConnectionRequestDeleteAPIView.as_view()


class JobReferralCreateView(CandidateRequiredMixin, FormView, JSONResponseMixin):
    """
    View for referring a job post to a team member.
    """
    model = JobReferral
    form_class = JobReferralForm

    def get_initial(self):
        return {'candidate': self.request.user.candidate}

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

job_referral_create = JobReferralCreateView.as_view()


class UserReferralCreateView(CandidateRequiredMixin, FormView, JSONResponseMixin):
    """
    View for referring a user to another user.
    """
    model = UserReferral
    form_class = UserReferralForm

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

user_referral_create = UserReferralCreateView.as_view()


class JobApplicationView(CandidateRequiredMixin, CreateView, JSONResponseMixin):
    """
    View for candidates applying to a job post.
    """
    model = JobApplication
    form_class = JobApplicationForm

    def get_initial(self):
        return {
            'job_post': JobPost.objects.get(uuid=self.kwargs.get('uuid'))
        }

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

job_application = JobApplicationView.as_view()


class SearchViewSet(viewsets.GenericViewSet):

    # GET /search/jobs/
    @list_route(methods=['get'], url_path='jobs')
    def job_list(self, request):
        """
        Gets the list of job posts from the search.
        """
        title = self.request.query_params.getlist('title', None)
        skills = self.request.query_params.getlist('skills', None)
        city = self.request.query_params.getlist('city', None)
        country = self.request.query_params.getlist('country', None)

        reversed_countries = {
            value.lower(): key.lower()
            for key, value in countries
        }

        search = title + skills + city + country
        if search:
            for item in search:
                country_search = reversed_countries.get(item.lower(), None)
                if country_search:
                    search.append(country_search)

            # generate SearchQuery item from search
            for index, item in enumerate(search):
                if index == 0:
                    search_query = SearchQuery(item)
                search_query |= SearchQuery(item)

            job_post = JobPost.objects\
                .annotate(search=SearchVector('title', 'skills__name', 'city', 'country'))\
                .filter(search=search_query)\
                .distinct('id')
        else:
            job_post = None

        return Response(JobPostSerializer(job_post, many=True).data)


class JobPostViewSet(viewsets.ViewSet):

    # GET /jobs/locations/
    @list_route(methods=['get'], url_path='locations')
    def list_locations(self, request):
        job_post = JobPost.objects.all()
        return Response(LocationSerializer(job_post).data)

    # GET /jobs/titles/
    @list_route(methods=['get'], url_path='titles')
    def list_titles(self, request):
        titles = JobPost.objects.all().distinct('title').values_list('title', flat=True)
        return Response(titles)

    # POST /jobs/<pk>/applications/
    @detail_route(methods=['post'], url_path='applications')
    def apply_job(self, request, pk=None):
        request.data.update({
            'job_post': pk,
            'candidate': request.user.candidate.pk,
        })
        serializer = JobApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # POST /jobs/<pk>/referrals/
    @detail_route(methods=['post'], url_path='referrals')
    def refer_job(self, request, pk=None):
        request.data.update({
            'job_post': pk,
            'referred_by': request.user.candidate.pk,
        })

        serializer = JobReferralSerializer(data=request.data, initial={'candidate': request.user.candidate})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # POST /jobs/<pk>/interests/
    @detail_route(methods=['post'], url_path='interests')
    def job_interests(self, request, pk=None):
        request.data.update({
            'job_post': pk,
            'candidate': request.user.candidate.pk,
        })

        interest = JobInterest.objects.filter(
            job_post__pk=pk,
            candidate=request.user.candidate.pk
        ).first()

        serializer = JobInterestSerializer(data=request.data, instance=interest)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
