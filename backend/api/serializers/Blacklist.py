from rest_framework import serializers
from api.models import Blacklist, CreditBureauCheck, DocumentVerification, AuditLog, BiometricData


class BlacklistSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    blacklisted_by_name = serializers.CharField(source='blacklisted_by.username', read_only=True)
    removed_by_name = serializers.CharField(source='removed_by.username', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    days_blacklisted = serializers.SerializerMethodField()
    
    class Meta:
        model = Blacklist
        fields = '__all__'
        read_only_fields = ['blacklisted_at', 'removed_at', 'created_at', 'updated_at']
    
    def get_days_blacklisted(self, obj):
        from django.utils import timezone
        if obj.is_active:
            delta = timezone.now() - obj.blacklisted_at
            return delta.days
        return None


class CreditBureauCheckSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CreditBureauCheck
        fields = '__all__'
        read_only_fields = ['created_at']


class DocumentVerificationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVerification
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at']
    
    def get_document_url(self, obj):
        if obj.document_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document_file.url)
        return None


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['created_at']


class BiometricDataSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    biometric_type_display = serializers.CharField(source='get_biometric_type_display', read_only=True)
    
    class Meta:
        model = BiometricData
        fields = '__all__'
        read_only_fields = ['registered_at', 'last_used']
        extra_kwargs = {
            'biometric_hash': {'write_only': True}  # Never return raw biometric data
        }
