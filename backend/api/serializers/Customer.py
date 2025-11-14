from rest_framework import serializers
from ..models.Customer import Customer

class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    total_loans = serializers.SerializerMethodField()
    total_loan_amount = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id',
            'account',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_selfie',
            'national_id_front',
            'national_id_back',
            'proof_of_address',
            'country',
            'city',
            'state',
            'postal_code',
            'address',
            'gender',
            'date_of_birth',
            'place_of_birth',
            'education_degree',
            'job_status',
            'material_status',
            'salary_range',
            'total_loans',
            'total_loan_amount',
            'account_status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_email(self, obj):
        return obj.account.user.email if hasattr(obj, 'account') else None
    
    def get_phone(self, obj):
        # Add when phone field is available
        return None
    
    def get_total_loans(self, obj):
        return obj.loan_set.count()
    
    def get_total_loan_amount(self, obj):
        from django.db.models import Sum
        total = obj.loan_set.aggregate(total=Sum('amount'))['total']
        return str(total) if total else "0.00"
    
    def get_account_status(self, obj):
        return obj.account.status if hasattr(obj, 'account') else None
