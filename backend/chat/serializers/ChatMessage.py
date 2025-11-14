from rest_framework import serializers
from chat.models.ChatMessage import ChatMessage
from django.contrib.auth.models import User


class MessageSenderSerializer(serializers.ModelSerializer):
    """Serializer for message sender info"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ChatMessageSerializer(serializers.ModelSerializer):
    """Enhanced serializer for chat messages with sender and reply info"""
    sender = MessageSenderSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    reply_to = serializers.SerializerMethodField()
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conversation', 'sender', 'sender_id', 'type', 'text',
            'attachments', 'reply_to_message', 'reply_to', 'thread_id',
            'reactions', 'read_receipts', 'edited', 'edited_at',
            'created_at', 'deleted', 'delivery_status', 'sync_status',
            'metadata', 'is_own_message'
        ]
        read_only_fields = ['created_at', 'edited_at']
    
    def get_reply_to(self, obj):
        if obj.reply_to_message:
            return {
                'id': obj.reply_to_message.id,
                'text': obj.reply_to_message.text,
                'sender': MessageSenderSerializer(obj.reply_to_message.sender).data
            }
        return None
    
    def get_is_own_message(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender.id == request.user.id
        return False


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""
    class Meta:
        model = ChatMessage
        fields = [
            'conversation', 'text', 'type', 'attachments',
            'reply_to_message', 'thread_id', 'metadata'
        ]
