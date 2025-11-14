from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from api.models.Loan import Loan
from api.utils.websocket_utils import trigger_loan_status_change

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'borrower_name',
        'loan_type',
        'formatted_amount',
        'interest_rate',
        'period_months',
        'status_badge',
        'repayment_progress_bar',
        'remaining_balance_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'loan_type',
        'created_at',
        'start_date',
        'end_date',
        ('borrower', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'borrower__first_name',
        'borrower__last_name',
        'borrower__account__email',
        'id',
        'purpose_description'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'total_amount',
        'monthly_payment',
        'repayment_progress',
        'loan_details_summary'
    ]
    
    fieldsets = (
        ('Borrower Information', {
            'fields': ('borrower',)
        }),
        ('Loan Details', {
            'fields': (
                'loan_type',
                'amount',
                'interest_rate',
                'period_months',
                'purpose_description',
                'billing_address'
            )
        }),
        ('Calculated Amounts', {
            'fields': (
                'monthly_payment',
                'total_amount',
                'remaining_balance',
                'repayment_progress',
            ),
            'classes': ('collapse',)
        }),
        ('Repayment Schedule', {
            'fields': (
                'next_payment_amount',
                'next_payment_date',
                'agreement_date',
                'start_date',
                'end_date'
            )
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Additional Information', {
            'fields': (
                'repayment_methods',
                'loan_details_summary',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'approve_loans',
        'reject_loans',
        'disburse_loans',
        'mark_as_active',
        'close_loans',
        'calculate_loan_details_action'
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    
    # Custom display methods
    def borrower_name(self, obj):
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"
    borrower_name.short_description = 'Borrower'
    borrower_name.admin_order_field = 'borrower__first_name'
    
    def formatted_amount(self, obj):
        return format_html('<strong>R {:,.2f}</strong>', obj.amount)
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'APPROVED': '#4CAF50',
            'REJECTED': '#F44336',
            'DISBURSED': '#2196F3',
            'ACTIVE': '#4CAF50',
            'CLOSED': '#9E9E9E'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def repayment_progress_bar(self, obj):
        progress = obj.repayment_progress
        color = '#4CAF50' if progress >= 50 else '#FFA500' if progress >= 25 else '#F44336'
        return format_html(
            '<div style="width:100px; background-color:#f0f0f0; border-radius:3px;">'
            '<div style="width:{}px; background-color:{}; height:20px; border-radius:3px; text-align:center; color:white; font-size:11px; line-height:20px;">'
            '{}%</div></div>',
            progress,
            color,
            progress
        )
    repayment_progress_bar.short_description = 'Progress'
    
    def remaining_balance_display(self, obj):
        return format_html('R {:,.2f}', obj.remaining_balance)
    remaining_balance_display.short_description = 'Remaining'
    remaining_balance_display.admin_order_field = 'remaining_balance'
    
    def loan_details_summary(self, obj):
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Total Amount:</strong></td><td>R {:,.2f}</td></tr>'
            '<tr><td><strong>Monthly Payment:</strong></td><td>R {:,.2f}</td></tr>'
            '<tr><td><strong>Remaining Balance:</strong></td><td>R {:,.2f}</td></tr>'
            '<tr><td><strong>Progress:</strong></td><td>{}%</td></tr>'
            '</table>',
            obj.total_amount,
            obj.monthly_payment,
            obj.remaining_balance,
            obj.repayment_progress
        )
    loan_details_summary.short_description = 'Loan Summary'
    
    # Admin actions
    def approve_loans(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='APPROVED')
        for loan in queryset.filter(status='APPROVED'):
            trigger_loan_status_change(loan, 'APPROVED', 'Your loan has been approved!')
        self.message_user(request, f'{updated} loans approved successfully.')
    approve_loans.short_description = 'Approve selected loans'
    
    def reject_loans(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        for loan in queryset.filter(status='REJECTED'):
            trigger_loan_status_change(loan, 'REJECTED', 'Your loan has been rejected.')
        self.message_user(request, f'{updated} loans rejected.')
    reject_loans.short_description = 'Reject selected loans'
    
    def disburse_loans(self, request, queryset):
        updated = queryset.filter(status='APPROVED').update(status='DISBURSED')
        for loan in queryset.filter(status='DISBURSED'):
            trigger_loan_status_change(loan, 'DISBURSED', 'Your loan has been disbursed!')
        self.message_user(request, f'{updated} loans disbursed successfully.')
    disburse_loans.short_description = 'Disburse approved loans'
    
    def mark_as_active(self, request, queryset):
        updated = queryset.filter(status='DISBURSED').update(status='ACTIVE')
        self.message_user(request, f'{updated} loans marked as active.')
    mark_as_active.short_description = 'Mark as active'
    
    def close_loans(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(request, f'{updated} loans closed.')
    close_loans.short_description = 'Close selected loans'
    
    def calculate_loan_details_action(self, request, queryset):
        for loan in queryset:
            loan.calculate_loan_details()
        self.message_user(request, f'Loan details calculated for {queryset.count()} loans.')
    calculate_loan_details_action.short_description = 'Calculate loan details'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Calculate loan details on save
        obj.calculate_loan_details()
        
        # Trigger WebSocket update if status changed
        if change and 'status' in form.changed_data:
            trigger_loan_status_change(obj, obj.status)

