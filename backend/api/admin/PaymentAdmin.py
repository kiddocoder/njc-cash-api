from django.contrib import admin
from django.utils.html import format_html
from api.models.Payment import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'loan_display',
        'payment_method_display',
        'formatted_amount',
        'status_badge',
        'payment_date',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'payment_date',
        'created_at',
        ('loan', admin.RelatedOnlyFieldListFilter),
        ('payment_method', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'loan__borrower__first_name',
        'loan__borrower__last_name',
        'transaction_reference',
        'notes'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'transaction_reference']
    
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'loan',
                'payment_method',
                'amount',
                'payment_date',
                'status'
            )
        }),
        ('Transaction', {
            'fields': (
                'transaction_reference',
                'notes'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_successful', 'mark_as_failed', 'process_refunds']
    
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    def loan_display(self, obj):
        return f"Loan #{obj.loan.id} - {obj.loan.borrower.first_name} {obj.loan.borrower.last_name}"
    loan_display.short_description = 'Loan'
    
    def payment_method_display(self, obj):
        if obj.payment_method:
            return obj.payment_method.get_payment_type_display()
        return 'N/A'
    payment_method_display.short_description = 'Method'
    
    def formatted_amount(self, obj):
        return format_html('<strong>R {:,.2f}</strong>', obj.amount)
    formatted_amount.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'SUCCESSFUL': '#4CAF50',
            'FAILED': '#F44336',
            'REFUNDED': '#9C27B0'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_successful(self, request, queryset):
        updated = queryset.update(status='SUCCESSFUL')
        self.message_user(request, f'{updated} payments marked as successful.')
    mark_as_successful.short_description = 'Mark as successful'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_as_failed.short_description = 'Mark as failed'
    
    def process_refunds(self, request, queryset):
        updated = queryset.filter(status='SUCCESSFUL').update(status='REFUNDED')
        self.message_user(request, f'{updated} payments refunded.')
    process_refunds.short_description = 'Process refunds'
