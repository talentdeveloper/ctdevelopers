import email
import json
import sys
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import(
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    View,
)
from django.http import JsonResponse
from django.views.generic.list import ListView
from .forms import VirtualAliasForm
from .models import (
    EmailAlert,
    VirtualAlias,
)

from users.mixins import ProfileCompleteRequiredMixin
from django.shortcuts import render


User = get_user_model()


class AlertListView(ProfileCompleteRequiredMixin, ListView):
    model = EmailAlert
    template_name = 'mail/alert_list.html'

    def get_context_data(self, **kwargs):
        context = super(AlertListView, self).get_context_data(**kwargs)
        favourite = self.request.GET.get('favourite')
        unfavourite = self.request.GET.get('unfavourite')

        if favourite:
            EmailAlert.objects.filter(id=favourite).update(favourite=True)
        if unfavourite:
            EmailAlert.objects.filter(id=unfavourite).update(favourite=False)

        aliases = VirtualAlias.objects.filter(user_id=self.request.user.id).values_list('source', flat=True)
        if aliases:
            context['aliases'] = True
            context['alerts_active'] = VirtualAlias.objects.filter(user_id=self.request.user.id)
            context['alert_groups'] = EmailAlert.objects.filter(to_field__in=aliases).values('from_contact_email').distinct()
            context['messages'] = False
            messages = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date')

            if messages:
                context['messages'] = True
                context['no_msg'] = False
                if self.request.GET.get('showfavourites'):
                    context['messages'] = EmailAlert.objects.filter(to_field__in=aliases, favourite=True).order_by('-message_date')
                    context['first_message'] = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date').first()
                elif self.request.GET.get('message'):
                    try:
                        context['messages'] = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date')
                        context['first_message'] = EmailAlert.objects.get(to_field__in=aliases, id=self.request.GET.get('message'))
                    except:
                        context['no_msg'] = True
                elif self.request.GET.get('alerts'):
                    context['messages'] = EmailAlert.objects.filter(to_field=self.request.GET.get('alerts')).order_by('-message_date')
                    context['first_message'] = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date').first()
                else:
                    context['first_message'] = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date').first()
                    context['messages'] = EmailAlert.objects.filter(to_field__in=aliases).order_by('-message_date')
        else:
            context['aliases'] = False
        return context

alert_list = AlertListView.as_view()


class AlertDetailView(ProfileCompleteRequiredMixin, DetailView):
    model = EmailAlert
    context_object_name = 'alert'
    template_name = 'mail/alert_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AlertDetailView, self).get_context_data(**kwargs)
        aliases = VirtualAlias.objects.filter(user_id=self.request.user.id).values_list('source', flat=True)
        try:
            message = EmailAlert.objects.get(to_field__in=aliases, id=self.kwargs.get('pk'))
        except:
            context['no_msg'] = True
        if message:
            msg = email.message_from_string(message.message)
            if msg.is_multipart():
                for payload in msg.get_payload():
                    clean_body = payload.get_payload(decode=True)
            else:
                clean_body = msg.get_payload(decode=True)

            context['message'] = message
            context['body'] = clean_body
        return context

alert_detail = AlertDetailView.as_view()


class FavouriteView(ProfileCompleteRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        mail_id = request.POST['mail_id']
        mail = get_object_or_404(EmailAlert, id=mail_id)
        mail.favourite = not mail.favourite
        mail.save()

        json_response = {
            'message': {
                'favourite': mail.favourite,
                'subject': mail.subject,
                'from_contact_email': mail.from_contact_email,
                'message_date': str(mail.message_date),
                'to_field': mail.to_field,
            },
        }
        return JsonResponse(json_response)

favourite_view = FavouriteView.as_view()


class VirtualAliasListView(ProfileCompleteRequiredMixin, CreateView):
    model = VirtualAlias
    form_class = VirtualAliasForm
    template_name = 'mail/virtual_alias_list.html'
    success_url = reverse_lazy('mail:virtual_alias_list')

    def get_initial(self):
        return {'user': self.request.user}

    def get_context_data(self, **kwargs):
        context = super(VirtualAliasListView, self).get_context_data(**kwargs)
        context['virtual_aliases'] = VirtualAlias.objects.filter(user_id=self.request.user.id)
        return context

virtual_alias_list = VirtualAliasListView.as_view()


class VirtualAliasUpdate(ProfileCompleteRequiredMixin, UpdateView):
    model = VirtualAlias
    fields = ['source',]

virtual_alias_update = VirtualAliasUpdate.as_view()


class VirtualAliasDelete(ProfileCompleteRequiredMixin, DeleteView):
    model = VirtualAlias
    template_name = 'mail/virtual_alias_confirm_delete.html'
    success_url = reverse_lazy('mail:virtual_alias_list')

virtual_alias_delete = VirtualAliasDelete.as_view()
