from django import forms
from django.contrib.auth import get_user_model
#from django.utils.translation import ugettext_lazy as _

from .models import Issue

User = get_user_model()


class IssueForm(forms.ModelForm):

    class Meta:
        model = Issue
        fields = ('subject', 'description', 'client', 'provider')
        widgets = {
            'client': forms.HiddenInput(),
            'provider': forms.HiddenInput()
        }
