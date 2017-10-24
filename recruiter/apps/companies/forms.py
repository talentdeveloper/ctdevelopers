from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .models import (
    Company,
    CompanyInvitation,
)
from core.utils import send_email_template


User = get_user_model()


class CompanyUpdateForm(forms.ModelForm):

    class Meta:
        model = Company
        exclude = ['owner', 'date_updated', 'status', 'slug', 'company_type',]


class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name', 'domain', 'city', 'country',]

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        self.user = initial.get('user')

    def save(self, *args, **kwargs):
        company = super(CompanyForm, self).save(commit=False)
        company.owner = self.user
        company.save()

        self.user.profile.company = company
        self.user.profile.save()

        return company


class CompanyInvitationForm(forms.ModelForm):

    class Meta:
        model = CompanyInvitation
        fields = ('invitee_email',)

    def __init__(self, *args, **kwargs):
        super(CompanyInvitationForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        self.inviter = initial.get('inviter')

    def clean_invitee_email(self):
        invitee_email = self.cleaned_data.get('invitee_email')
        domain = invitee_email[invitee_email.find('@') + 1:]

        if domain != self.inviter.profile.company.domain:
            raise forms.ValidationError(
                _('You are only allowed to invite users with email having the same company domain.'),
                code='invalid-domain'
            )

        if User.objects.filter(email=invitee_email).exists():
            raise forms.ValidationError(
                _('This email already exists.'),
                code='duplicate-user-email'
            )

        return invitee_email

    def save(self, *args, **kwargs):
        company_invitation = super(CompanyInvitationForm, self).save(commit=False)
        company_invitation.inviter = self.inviter
        company_invitation.save()

        send_email_template(
            subject=_('Company Invitation, SquareBalloon'),
            template='companies/email/company_invitation.html',
            recipient=[company_invitation.invitee_email,],
            data={
                'company_invitation': company_invitation,
            },
        )

        return company_invitation
