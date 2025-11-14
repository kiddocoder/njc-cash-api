from rest_framework import serializers
from ..models.NotificationPreference import NotificationPreference

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'user',
            'new_loan_application_email',
            'document_verification_email',
            'pending_approval_email',
            'client_messages_email',
            'payment_processing_email',
            'system_updates_email',
            'new_loan_application_push',
            'document_verification_push',
            'pending_approval_push',
            'client_messages_push',
            'payment_processing_push',
            'system_updates_push',
            'payment_due_sms',
            'loan_status_sms',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
