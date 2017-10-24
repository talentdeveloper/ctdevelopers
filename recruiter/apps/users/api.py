from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
    View,
)

from allauth.account.utils import send_email_confirmation
from braces.views import (
    JSONResponseMixin,
    LoginRequiredMixin,
)
from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import (
    detail_route,
    list_route,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .forms import (
    AgentPhotoUploadForm,
    CandidateCVUploadForm,
    CandidateForm,
    CandidatePhotoUploadForm,
    CVRequestForm,
    SupportPhotoUploadForm,
    UserNoteForm,
)
from .mixins import CandidateRequiredMixin
from .models import (
    Candidate,
    CVRequest,
    UserNote,
)
from .serializers import (
    AgentSerializer,
    CandidateSerializer,
    SupportSerializer,
)
from chat.models import (
    Conversation,
    Message,
)
from recruit.models import Connection


User = get_user_model()


class ProfilePhotoUploadAPIView(LoginRequiredMixin, View):
    """
    View for uploading a user's profile picture.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            form = CandidatePhotoUploadForm(form_values, request.FILES, instance=request.user.profile)
        elif request.user.account_type == User.ACCOUNT_AGENT:
            form = AgentPhotoUploadForm(form_values, request.FILES, instance=request.user.profile)
        elif request.user.account_type == User.ACCOUNT_SUPPORT:
            form = SupportPhotoUploadForm(form_values, request.FILES, instance=request.user.profile)

        if form.is_valid():
            profile = form.save()

            connections = Connection.objects.filter(Q(connecter=request.user) | Q(connectee=request.user))
            return JsonResponse({
                'success': True,
                'image': profile.photo.url,
                'has_connections': connections.exists(),
            })


profile_photo_upload = ProfilePhotoUploadAPIView.as_view()


class ProfileCVUploadAPIView(CandidateRequiredMixin, View):
    """
    View for uploading a candidate's CV.
    """
    def post(self, request, **kwargs):
        # show profile dashboard according to user role
        # start with candidate profile
        form_values = request.POST.copy()
        form_values['user'] = request.user.id
        candidate = request.user.candidate
        form = CandidateCVUploadForm(form_values, request.FILES, instance=candidate)

        if form.is_valid():
            candidate = form.save(commit=True)
            return JsonResponse({'success': True, 'cv': candidate.cv.url})

profile_cv_upload = ProfileCVUploadAPIView.as_view()


class CandidateProfileDetailUpdateAPIView(CandidateRequiredMixin, UpdateView, JSONResponseMixin):
    """
    View for updating the candidate's profile through the profile page.
    """
    model = Candidate
    form_class = CandidateForm

    def get_object(self):
        return Candidate.objects.get(pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        form.save()
        connections = Connection.objects.filter(Q(connecter=self.request.user) | Q(connectee=self.request.user))

        return self.render_json_response({
            'success': True,
            'has_connections': connections.exists(),
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
            'formset': {
                'non_form_errors': form.candidate_skill_formset.non_form_errors(),
                'field_errors': form.candidate_skill_formset.errors,
            },
        })

candidate_profile_detail_update = CandidateProfileDetailUpdateAPIView.as_view()


class UserNoteCreateAPIView(LoginRequiredMixin, CreateView, JSONResponseMixin):
    """
    View for adding a note on a user.
    """
    model = UserNote
    form_class = UserNoteForm

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        user_note = form.save()
        return self.render_json_response({
            'success': True,
            'data': {
                'pk': user_note.pk,
                'note_to': {
                    'pk': user_note.note_to.pk,
                },
                'type': user_note.type,
                'text': user_note.text,
                'created_at': {
                    'proper': date(user_note.created_at, 'D, F d, o P'),
                    'timeago': naturaltime(user_note.created_at),
                },
                'csrf_token': get_token(self.request),
            }
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

user_note_create = UserNoteCreateAPIView.as_view()


class UserNoteUpdateAPIView(LoginRequiredMixin, UpdateView, JSONResponseMixin):
    """
    View for updating a note on a user.
    """
    model = UserNote
    form_class = UserNoteForm

    def get_object(self):
        return UserNote.objects.get(pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        user_note = form.save()
        return self.render_json_response({
            'success': True,
            'data': {
                'pk': user_note.pk,
                'note_to': {
                    'pk': user_note.note_to.pk,
                },
                'type': user_note.type,
                'text': user_note.text,
                'created_at': {
                    'proper': date(user_note.created_at, 'D, F d, o P'),
                    'timeago': naturaltime(user_note.created_at),
                },
            }
        })

    def form_invalid(self, form):
        return self.render_json_response({
            'success': False,
            'errors': form.errors,
        })

user_note_update = UserNoteUpdateAPIView.as_view()


class UserNoteDeleteAPIView(LoginRequiredMixin, DeleteView, JSONResponseMixin):
    """
    View for deleting a note on a user.
    """
    model = UserNote

    def get_object(self):
        return UserNote.objects.get(pk=self.kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        return self.render_json_response({'success': True})

user_note_delete = UserNoteDeleteAPIView.as_view()


class TrackingAPIView(LoginRequiredMixin, View, JSONResponseMixin):
    """
    View for returning the tracking details for a user.
    """
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs.get('pk'))

        user_notes = UserNote.objects.filter(note_to=user, note_by=self.request.user).order_by('-created_at')

        messages = Message.objects\
            .filter(conversation__users=user)\
            .filter(conversation__conversation_type=Conversation.CONVERSATION_USER)\
            .order_by('created_at')

        sent = messages.filter(author=self.request.user)
        first_contact_sent = sent.first()
        last_message_sent = sent.last()

        received = messages.exclude(author=self.request.user)
        last_message_received = received.last()

        data = {
            'auto_tracking': {
                'first_contact_sent': first_contact_sent.created_at.strftime('%d/%m/%y') if first_contact_sent else None,
                'last_message_sent': last_message_sent.created_at.strftime('%d/%m/%y') if last_message_sent else None,
                'last_message_received': last_message_received.created_at.strftime('%d/%m/%y') if last_message_received else None,
            },
            'user_notes': [
                {
                    'pk': user_note.pk,
                    'note_to': {
                        'pk': user_note.note_to.pk,
                    },
                    'type': user_note.type,
                    'text': user_note.text,
                    'created_at': {
                        'proper': date(user_note.created_at, 'D, F d, o P'),
                        'timeago': naturaltime(user_note.created_at),
                    },
                    'csrf_token': get_token(self.request),
                }
                for user_note in user_notes
            ]
        }
        return self.render_json_response({'data': data})

tracking = TrackingAPIView.as_view()


class CVRequestUpdateView(LoginRequiredMixin, UpdateView, JSONResponseMixin):
    """
    View for the CV Request.
    """
    model = CVRequest
    form_class = CVRequestForm

    def get_object(self):
        return CVRequest.objects.get(uuid=self.kwargs.get('uuid'))

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

cv_request_update = CVRequestUpdateView.as_view()


class UsersViewSet(viewsets.ViewSet):

    # GET /users/me/
    @list_route(methods=['get'], url_path='me')
    def current(self, request):
        if request.user.account_type == User.ACCOUNT_CANDIDATE:
            serializer = CandidateSerializer(request.user.profile)
        elif request.user.account_type == User.ACCOUNT_AGENT:
            serializer = AgentSerializer(request.user.profile)
        elif request.user.account_type == User.ACCOUNT_SUPPORT:
            serializer = SupportSerializer(request.user.profile)

        return Response(serializer.data)

    # PATCH /users/me/
    @list_route(methods=['get'], url_path='me')
    def patch(self, request, pk=None):
        user = request.user
        if user.account_type == User.ACCOUNT_CANDIDATE:
            serializer = CandidateSerializer(data=request.data, instance=user.profile, partial=True)
        elif user.account_type == User.ACCOUNT_AGENT:
            serializer = AgentSerializer(data=request.data, instance=user.profile, partial=True)
        elif user.account_type == User.ACCOUNT_SUPPORT:
            serializer = SupportSerializer(data=request.data, instance=user.profile, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



class AccountsViewSet(viewsets.ViewSet):

    permission_classes = (AllowAny,)

    # POST /accounts/<pk>/email/verify/send/
    @detail_route(methods=['post'], url_path='email/verify/send')
    def send_email_verification(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        send_email_confirmation(request, user, signup=True)

        return Response({'detail': 'Email verifcation sent.'})
