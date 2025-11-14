from django.contrib import admin
from ..models.Repayment import Repayment

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'loan',
        'due_date',
        'amount_due',
        'amount_paid',
        'status',
        'payment_date'
    ]
    list_filter = ['status', 'due_date', 'payment_date']
    search_fields = [
        'loan__borrower__first_name',
        'loan__borrower__last_name',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    ordering = ['due_date']
