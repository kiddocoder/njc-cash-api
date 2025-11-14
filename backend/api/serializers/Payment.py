from rest_framework import serializers
from ..models.Payment import Payment

class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    loan_type = serializers.SerializerMethodField()
    formatted_amount = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'loan',
            'customer',
            'customer_name',
            'loan_type',
            'payment_method',
            'payment_method_display',
            'amount',
            'formatted_amount',
            'status',
            'payment_type',
            'transaction_id',
            'reference_number',
            'notes',
            'processed_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'transaction_id']
    
    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    
    def get_loan_type(self, obj):
        return obj.loan.get_loan_type_display()
    
    def get_formatted_amount(self, obj):
        return f"R {obj.amount:,.2f}"
    
    def get_payment_method_display(self, obj):
        if obj.payment_method:
            if obj.payment_method.type == 'CARD':
                return f"{obj.payment_method.card_type} •••• {obj.payment_method.card_last_four}"
            elif obj.payment_method.type == 'BANK_ACCOUNT':
                return f"{obj.payment_method.bank_name}"
            else:
                return f"{obj.payment_method.mobile_provider}"
        return None
