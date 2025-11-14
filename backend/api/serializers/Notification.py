from rest_framework import serializers
from ..models.Notification import Notification

class NotificationSerializer(serializers.ModelSerializer):
    formatted_amount = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'type',
            'title',
            'message',
            'loan',
            'conversation',
            'amount',
            'formatted_amount',
            'is_read',
            'read_at',
            'action_text',
            'action_url',
            'created_at',
            'time_ago'
        ]
        read_only_fields = ['created_at']
    
    def get_formatted_amount(self, obj):
        if obj.amount:
            prefix = "+" if obj.amount > 0 else ""
            return f"{prefix}R {obj.amount:,.2f}"
        return None
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")
