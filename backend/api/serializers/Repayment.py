from rest_framework import serializers
from ..models.Repayment import Repayment

class RepaymentSerializer(serializers.ModelSerializer):
    loan_borrower_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Repayment
        fields = [
            'id',
            'loan',
            'loan_borrower_name',
            'due_date',
            'amount_due',
            'amount_paid',
            'remaining_balance',
            'status',
            'payment_date',
            'payment_method',
            'notes',
            'is_overdue',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_loan_borrower_name(self, obj):
        return f"{obj.loan.borrower.first_name} {obj.loan.borrower.last_name}"
    
    def get_is_overdue(self, obj):
        from datetime import date
        return obj.due_date < date.today() and obj.status == 'PENDING'
    
    def get_remaining_balance(self, obj):
        return obj.amount_due - obj.amount_paid
