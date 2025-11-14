from rest_framework import serializers
from api.models import EwalletPayment


class EwalletPaymentSerializer(serializers.ModelSerializer):
    loan_reference = serializers.CharField(source='loan.loan_id', read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = EwalletPayment
        fields = '__all__'
        read_only_fields = [
            'initiated_at', 'completed_at', 'failed_at',
            'created_at', 'updated_at', 'provider_transaction_id'
        ]
