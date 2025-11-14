from rest_framework import serializers
from chat.models.Conversation import Conversation
from chat.models.ChatMessage import ChatMessage
from django.contrib.auth.models import User


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for conversation participants"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ConversationSerializer(serializers.ModelSerializer):
    """Enhanced serializer for conversations with participant and message info"""
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        source='participants',
        write_only=True
    )
    last_message_text = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'image_url', 'participants', 'participant_ids',
            'admin_ids', 'last_message', 'last_message_text', 'last_message_sender',
            'last_message_time', 'unread_count', 'participant_count',
            'created_at', 'updated_at', 'muted', 'metadata'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_last_message_text(self, obj):
        if obj.last_message:
            return obj.last_message.text
        return None
    
    def get_last_message_sender(self, obj):
        if obj.last_message:
            sender = obj.last_message.sender
            return f"{sender.first_name} {sender.last_name}".strip() or sender.username
        return None
    
    def get_last_message_time(self, obj):
        if obj.last_message:
            return obj.last_message.created_at.isoformat()
        return None
    
    def get_unread_count(self, obj):
        # Get unread count for current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ChatMessage.objects.filter(
                conversation=obj,
                delivery_status__in=['SENT', 'DELIVERED']
            ).exclude(sender=request.user).count()
        return 0
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for conversation lists"""
    last_message_text = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'image_url', 'last_message_text',
            'last_message_time', 'unread_count', 'muted', 'updated_at'
        ]
    
    def get_last_message_text(self, obj):
        if obj.last_message:
            return obj.last_message.text[:100]  # Truncate for list view
        return None
    
    def get_last_message_time(self, obj):
        if obj.last_message:
            return obj.last_message.created_at.isoformat()
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ChatMessage.objects.filter(
                conversation=obj,
                delivery_status__in=['SENT', 'DELIVERED']
            ).exclude(sender=request.user).count()
        return 0
