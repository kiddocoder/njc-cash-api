from rest_framework import serializers
from ..models.PaymentMethod import PaymentMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'customer',
            'type',
            'card_type',
            'card_last_four',
            'card_expiry',
            'bank_name',
            'account_number',
            'mobile_provider',
            'mobile_number',
            'is_default',
            'is_active',
            'display_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_display_name(self, obj):
        if obj.type == 'CARD':
            return f"{obj.card_type} •••• {obj.card_last_four}"
        elif obj.type == 'BANK_ACCOUNT':
            return f"{obj.bank_name} •••• {obj.account_number[-4:]}"
        else:
            return f"{obj.mobile_provider} - {obj.mobile_number}"
