from django import forms
from django.forms import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from .models import VirtualAlias


class VirtualAliasForm(forms.ModelForm):

    class Meta:
        model = VirtualAlias
        fields = ('name', 'site', 'source',)

    def __init__(self, *args, **kwargs):
        super(VirtualAliasForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        self.user = initial.get('user')
        self.fields['name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['site'].widget.attrs.update({'class' : 'form-control'})
        self.fields['source'].widget.attrs.update({'class' : 'form-control'})

    def clean_source(self):
        source = '{}.{}@squareballoon.com'.format(self.cleaned_data.get('source'), self.user.username)

        if VirtualAlias.objects.filter(source=source).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))

        return source

    def save(self, *args, **kwargs):
        alias = super(VirtualAliasForm, self).save(commit=False)
        alias.source = self.cleaned_data.get('source')
        alias.destination = 'incoming@squareballoon.com'
        alias.domain = 1
        alias.user_id = self.user.id
        alias.save()

        return alias
