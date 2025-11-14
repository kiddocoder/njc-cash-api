from rest_framework import serializers
from ..models.UserSession import UserSession

class UserSessionSerializer(serializers.ModelSerializer):
    device_display = serializers.SerializerMethodField()
    login_time = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id',
            'user',
            'session_key',
            'device_name',
            'device_type',
            'device_display',
            'os_name',
            'os_version',
            'browser_name',
            'browser_version',
            'ip_address',
            'country',
            'city',
            'is_active',
            'last_activity',
            'created_at',
            'login_time',
            'expires_at'
        ]
        read_only_fields = ['created_at', 'last_activity']
    
    def get_device_display(self, obj):
        if obj.device_name:
            return obj.device_name
        elif obj.browser_name and obj.os_name:
            return f"{obj.os_name}, {obj.browser_name}"
        return "Unknown Device"
    
    def get_login_time(self, obj):
        return obj.created_at.strftime("%d/%m/%Y at %H:%M")
