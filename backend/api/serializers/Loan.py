from rest_framework import serializers
from ..models.Loan import Loan
from ..models.Customer import Customer

class LoanSerializer(serializers.ModelSerializer):
    borrower_name = serializers.SerializerMethodField()
    borrower_email = serializers.SerializerMethodField()
    borrower_phone = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    formatted_amount = serializers.SerializerMethodField()
    formatted_remaining_balance = serializers.SerializerMethodField()
    formatted_next_payment = serializers.SerializerMethodField()
    formatted_monthly_payment = serializers.SerializerMethodField()
    formatted_total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id',
            'borrower',
            'borrower_name',
            'borrower_email',
            'borrower_phone',
            'loan_type',
            'amount',
            'formatted_amount',
            'interest_rate',
            'period_months',
            'monthly_payment',
            'formatted_monthly_payment',
            'total_amount',
            'formatted_total_amount',
            'remaining_balance',
            'formatted_remaining_balance',
            'repayment_progress',
            'next_payment_amount',
            'formatted_next_payment',
            'next_payment_date',
            'agreement_date',
            'status',
            'start_date',
            'end_date',
            'days_until_due',
            'purpose_description',
            'billing_address',
            'repayment_methods',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_borrower_name(self, obj):
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"
    
    def get_borrower_email(self, obj):
        return obj.borrower.account.user.email if hasattr(obj.borrower, 'account') else None
    
    def get_borrower_phone(self, obj):
        return None
    
    def get_days_until_due(self, obj):
        from datetime import date
        if obj.end_date:
            delta = obj.end_date - date.today()
            return delta.days
        return None
    
    def get_formatted_amount(self, obj):
        return f"R {obj.amount:,.2f}"
    
    def get_formatted_remaining_balance(self, obj):
        return f"R {obj.remaining_balance:,.2f}"
    
    def get_formatted_next_payment(self, obj):
        return f"R {obj.next_payment_amount:,.2f}"
    
    def get_formatted_monthly_payment(self, obj):
        return f"R {obj.monthly_payment:,.2f}"
    
    def get_formatted_total_amount(self, obj):
        return f"R {obj.total_amount:,.2f}"

class LoanDetailSerializer(LoanSerializer):
    payments_history = serializers.SerializerMethodField()
    
    class Meta(LoanSerializer.Meta):
        fields = LoanSerializer.Meta.fields + ['payments_history']
    
    def get_payments_history(self, obj):
        from .Payment import PaymentSerializer
        payments = obj.payments.all()[:10]  # Last 10 payments
        return PaymentSerializer(payments, many=True).data
