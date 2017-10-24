from django.template import Library

from chat.models import Conversation


register = Library()


@register.assignment_tag
def get_user_conversation(user1, user2):
    return Conversation.objects\
        .filter(conversation_type=Conversation.CONVERSATION_USER)\
        .filter(users=user1)\
        .filter(users=user2).first()
