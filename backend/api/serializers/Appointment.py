from rest_framework import serializers
from ..models.Appointment import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer',
            'customer_name',
            'customer_email',
            'description',
            'scheduled_time',
            'status',
            'is_upcoming',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    
    def get_customer_email(self, obj):
        return obj.customer.account.user.email if hasattr(obj.customer, 'account') else None
    
    def get_is_upcoming(self, obj):
        from django.utils import timezone
        return obj.scheduled_time > timezone.now() and obj.status == 'SCHEDULED'
