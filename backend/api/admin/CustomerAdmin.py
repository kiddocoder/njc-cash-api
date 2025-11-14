from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from api.models.Customer import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'full_name',
        'email_display',
        'phone_display',
        'location',
        'total_loans',
        'total_loan_amount',
        'account_status',
        'created_at'
    ]
    
    list_filter = [
        'country',
        'gender',
        'job_status',
        'created_at',
        ('account', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'first_name',
        'last_name',
        'account__email',
        'account__phone_number',
        'national_id',
        'city',
        'address'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'customer_statistics',
        'profile_selfie_preview',
        'national_id_front_preview',
        'national_id_back_preview',
        'proof_of_address_preview'
    ]
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account',)
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'gender',
                'date_of_birth',
                'place_of_birth'
            )
        }),
        ('Contact & Location', {
            'fields': (
                'address',
                'city',
                'state',
                'postal_code',
                'country'
            )
        }),
        ('Employment & Financial', {
            'fields': (
                'job_status',
                'salary_range',
                'education_degree',
                'material_status'
            )
        }),
        ('Documents', {
            'fields': (
                'profile_selfie',
                'profile_selfie_preview',
                'national_id_front',
                'national_id_front_preview',
                'national_id_back',
                'national_id_back_preview',
                'proof_of_address',
                'proof_of_address_preview'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics & Metadata', {
            'fields': (
                'customer_statistics',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'export_customer_data',
        'verify_documents',
        'deactivate_accounts'
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    
    # Custom display methods
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def email_display(self, obj):
        return obj.account.email if hasattr(obj, 'account') else 'N/A'
    email_display.short_description = 'Email'
    
    def phone_display(self, obj):
        return obj.account.phone_number if hasattr(obj, 'account') else 'N/A'
    phone_display.short_description = 'Phone'
    
    def location(self, obj):
        return f"{obj.city}, {obj.country}"
    location.short_description = 'Location'
    
    def total_loans(self, obj):
        count = obj.loan_set.count()
        return format_html('<strong>{}</strong>', count)
    total_loans.short_description = 'Total Loans'
    
    def total_loan_amount(self, obj):
        total = obj.loan_set.aggregate(Sum('amount'))['amount__sum'] or 0
        return format_html('R {:,.2f}', total)
    total_loan_amount.short_description = 'Total Amount'
    
    def account_status(self, obj):
        if hasattr(obj, 'account'):
            status = 'Active' if obj.account.is_active else 'Inactive'
            color = '#4CAF50' if obj.account.is_active else '#F44336'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                color,
                status
            )
        return 'N/A'
    account_status.short_description = 'Status'
    
    def customer_statistics(self, obj):
        loans = obj.loan_set.all()
        total_loans = loans.count()
        active_loans = loans.filter(status='ACTIVE').count()
        total_borrowed = loans.aggregate(Sum('amount'))['amount__sum'] or 0
        total_remaining = loans.aggregate(Sum('remaining_balance'))['remaining_balance__sum'] or 0
        
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Total Loans:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Active Loans:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Total Borrowed:</strong></td><td>R {:,.2f}</td></tr>'
            '<tr><td><strong>Remaining Balance:</strong></td><td>R {:,.2f}</td></tr>'
            '</table>',
            total_loans,
            active_loans,
            total_borrowed,
            total_remaining
        )
    customer_statistics.short_description = 'Statistics'
    
    def profile_selfie_preview(self, obj):
        if obj.profile_selfie:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.profile_selfie.url)
        return "No image"
    profile_selfie_preview.short_description = 'Profile Selfie Preview'
    
    def national_id_front_preview(self, obj):
        if obj.national_id_front:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.national_id_front.url)
        return "No image"
    national_id_front_preview.short_description = 'ID Front Preview'
    
    def national_id_back_preview(self, obj):
        if obj.national_id_back:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.national_id_back.url)
        return "No image"
    national_id_back_preview.short_description = 'ID Back Preview'
    
    def proof_of_address_preview(self, obj):
        if obj.proof_of_address:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;" />', obj.proof_of_address.url)
        return "No image"
    proof_of_address_preview.short_description = 'Address Proof Preview'
    
    # Admin actions
    def export_customer_data(self, request, queryset):
        # This would implement CSV export
        self.message_user(request, f'Exporting data for {queryset.count()} customers.')
    export_customer_data.short_description = 'Export customer data'
    
    def verify_documents(self, request, queryset):
        self.message_user(request, f'Documents verified for {queryset.count()} customers.')
    verify_documents.short_description = 'Verify documents'
    
    def deactivate_accounts(self, request, queryset):
        for customer in queryset:
            if hasattr(customer, 'account'):
                customer.account.is_active = False
                customer.account.save()
        self.message_user(request, f'{queryset.count()} accounts deactivated.')
    deactivate_accounts.short_description = 'Deactivate accounts'
