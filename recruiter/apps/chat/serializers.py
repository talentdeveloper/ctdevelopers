from rest_framework import serializers

from .models import Attachment, Message


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True, many=False)
    conversation = serializers.StringRelatedField(read_only=True, many=False)
    group_invite = serializers.StringRelatedField(read_only=True, many=False)
    attachments = AttachmentSerializer(many=True)

    class Meta:
        model = Message
        fields = ('id', 'text', 'author', 'conversation', 'group_invite')
