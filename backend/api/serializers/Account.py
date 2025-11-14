from rest_framework import serializers
from ..models.Account import Account

class AccountSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id',
            'user',
            'username',
            'email',
            'full_name',
            'status',
            'kyc_status',
            'account_type',
            'referal_citizen',
            'loan_amount',
            'total_loans',
            'account_number',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'account_number']
        extra_kwargs = {
            'otp_code': {'write_only': True},
            'otp_created_at': {'write_only': True}
        }
    
    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
    def get_email(self, obj):
        return obj.user.email if obj.user else None
    
    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None
