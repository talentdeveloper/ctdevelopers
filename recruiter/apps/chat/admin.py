from django.contrib import admin

from chat.models import Conversation, GroupInvite, Message, Participant


admin.site.register(Conversation)
admin.site.register(GroupInvite)
admin.site.register(Message)
admin.site.register(Participant)
