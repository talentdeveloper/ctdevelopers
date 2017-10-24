from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import (
    Connection,
    ConnectionInvite,
    ConnectionRequest,
    JobApplication,
    JobPost,
    JobReferral,
    UserReferral,
)
from core.forms import NumberMultipleSelectField
from core.utils import send_email_template
from users.models import Candidate


User = get_user_model()


class JobPostForm(forms.ModelForm):
    """
    Form for Job Posts.
    """
    class Meta:
        model = JobPost
        exclude = ('posted_by', 'applications',)

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.agent = initial.get('agent')

    def save(self, *args, **kwargs):
        job_post = super(JobPostForm, self).save(commit=False)
        skills = self.cleaned_data.get('skills')

        if not self.instance.pk:
            job_post.posted_by = self.agent
        job_post.save()

        job_post.skills.clear()
        job_post.skills.set(skills)

        return job_post


class ConnectionRequestForm(forms.ModelForm):
    """
    Form for Connection Requests.
    """
    class Meta:
        model = ConnectionRequest
        fields = ('connectee', 'connection_type',)

    def __init__(self, *args, **kwargs):
        super(ConnectionRequestForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.user = initial.get('user')

    def clean(self):
        connectee = self.cleaned_data.get('connectee')

        connections = Connection.objects.filter(
            (Q(connecter=self.user) & Q(connectee=connectee)) |
            (Q(connecter=connectee) & Q(connectee=self.user))
        )

        if connections.exists():
            raise forms.ValidationError(_('You are already connected to this user.'))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        connection_request = super(ConnectionRequestForm, self).save(commit=False)

        if not self.instance.pk:
            connection_request.connecter = self.user
        connection_request.save()

        return connection_request


class ConnectionInviteForm(forms.ModelForm):
    """
    Form for Connection Invite.
    """
    ACCOUNT_CANDIDATE = 1
    ACCOUNT_AGENT = 2
    ACCOUNT_SUPPORT = 3
    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_CANDIDATE, _('Candidate')),
        (ACCOUNT_AGENT, _('Agent')),
        (ACCOUNT_SUPPORT, _('IT Support')),
    )
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = ConnectionInvite
        fields = ('connectee_email', 'connection_type',)

    def __init__(self, *args, **kwargs):
        super(ConnectionInviteForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            initial = self.initial
            self.user = initial.get('user')

    def clean_connectee_email(self):
        connectee_email = self.cleaned_data.get('connectee_email')

        if User.objects.filter(email=connectee_email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))

        return connectee_email

    def save(self, *args, **kwargs):
        connection_invite = super(ConnectionInviteForm, self).save(commit=False)
        account_type = self.cleaned_data.get('account_type')

        with transaction.atomic():
            if not self.instance.pk:
                connection_invite.connecter = self.user
                connection_invites = ConnectionInvite.objects.filter(connectee_email=connection_invite.connectee_email)
                if connection_invites.exists():
                    connection_invite.pk = connection_invites.first().pk
            connection_invite.save()

            send_email_template(
                subject=_('Invitation, SquareBalloon'),
                template='recruit/email/connection_invitation.html',
                recipient=[connection_invite.connectee_email,],
                data={
                    'connection_invite': connection_invite,
                    'account_type': account_type,
                    'user': User,
                },
            )

        return connection_invite


class JobReferralForm(forms.Form):
    """
    Form for referring a job post.
    """
    job_post = forms.IntegerField()
    refer_to = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(JobReferralForm, self).__init__(*args, **kwargs)
        initial = self.initial
        self.candidate = initial.get('candidate')
        connections = Connection.objects\
            .filter(Q(connecter=self.candidate.user) | Q(connectee=self.candidate.user))\
            .filter(connection_type=Connection.CONNECTION_TEAM)

        choices = []
        for connection in connections:
            if connection.connecter == self.candidate.user and connection.connectee.account_type == User.ACCOUNT_CANDIDATE:
                choices.append((connection.connectee.candidate.pk, connection.connectee.get_full_name()))
            elif connection.connectee == self.candidate.user and connection.connecter.account_type == User.ACCOUNT_CANDIDATE:
                choices.append((connection.connecter.candidate.pk, connection.connecter.get_full_name()))
        self.fields['refer_to'].choices = choices

    def clean_job_post(self):
        job_post = self.cleaned_data.get('job_post')
        return JobPost.objects.get(pk=job_post)

    def clean_refer_to(self):
        refer_to = self.cleaned_data.get('refer_to')
        return Candidate.objects.filter(pk__in=refer_to)

    def save(self, *args, **kwargs):
        refer_to = self.cleaned_data.get('refer_to')
        job_post = self.cleaned_data.get('job_post')

        referrals = [
            JobReferral(
                job_post=job_post,
                referred_by=self.candidate,
                referred_to=candidate,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            for candidate in refer_to
        ]
        JobReferral.objects.bulk_create(referrals)


class UserReferralForm(forms.Form):
    """
    Form for referring a user to another user.
    """
    referred_user = forms.IntegerField()
    refer_to = NumberMultipleSelectField()

    class Meta:
        model = UserReferral
        fields = ('referred_by', 'referred_user',)

    def __init__(self, *args, **kwargs):
        super(UserReferralForm, self).__init__(*args, **kwargs)
        initial = self.initial
        self.user = initial.get('user')

    def clean_referred_user(self):
        referred_user = self.cleaned_data.get('referred_user')
        return User.objects.get(pk=referred_user)

    def clean_refer_to(self):
        refer_to = self.cleaned_data.get('refer_to')
        return User.objects.filter(pk__in=refer_to)

    def save(self, *args, **kwargs):
        refer_to = self.cleaned_data.get('refer_to')
        referred_user = self.cleaned_data.get('referred_user')

        referrals = [
            UserReferral(
                referred_by=self.user,
                referred_to=user,
                referred_user=referred_user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            for user in refer_to
        ]
        UserReferral.objects.bulk_create(referrals)


class JobApplicationForm(forms.ModelForm):
    """
    Form for candidates applying to a job post.
    """

    class Meta:
        model = JobApplication
        fields = ('candidate',)

    def __init__(self, *args, **kwargs):
        super(JobApplicationForm, self).__init__(*args, **kwargs)
        initial = self.initial
        self.job_post = initial.get('job_post')

    def save(self, *args, **kwargs):
        job_application = super(JobApplicationForm, self).save(commit=False)
        job_application.job_post = self.job_post
        job_application.candidate = self.cleaned_data.get('candidate')
        job_application.save()

        return job_application
