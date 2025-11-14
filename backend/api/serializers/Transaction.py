from rest_framework import serializers
from ..models.Transaction import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    loan_id = serializers.SerializerMethodField()
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'loan',
            'loan_id',
            'customer',
            'customer_name',
            'transaction_type',
            'amount',
            'formatted_amount',
            'description',
            'reference_number',
            'payment_method',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    
    def get_loan_id(self, obj):
        return obj.loan.id
    
    def get_formatted_amount(self, obj):
        return f"R {obj.amount:,.2f}"
