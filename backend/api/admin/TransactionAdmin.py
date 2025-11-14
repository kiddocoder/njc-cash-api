from django.contrib import admin
from ..models.Transaction import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'transaction_type',
        'customer',
        'loan',
        'amount',
        'payment_method',
        'created_at'
    ]
    list_filter = ['transaction_type', 'payment_method', 'created_at']
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'reference_number',
        'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
