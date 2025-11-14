from django.contrib import admin
from django.utils.html import format_html
from api.models.Account import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_display',
        'user__email',
        'phone_number',
        'is_active_badge',
        'is_verified_badge',
        'role_badge',
        'last_login',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'is_verified',
        'role',
        'created_at',
        'last_login',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'email',
        'phone_number',
        'id'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login',
        'verification_token',
        'account_summary'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'phone_number'
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active',
                'is_verified',
                'role'
            )
        }),
        ('Security', {
            'fields': (
                'verification_token',
                'reset_password_token',
                'reset_password_expire'
            ),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': (
                'last_login',
                'created_at',
                'updated_at',
                'account_summary'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activate_accounts',
        'deactivate_accounts',
        'verify_accounts',
        'reset_verification'
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    
    # Custom display methods
    def user_display(self, obj):
        return obj.user.username if obj.user else 'N/A'
    user_display.short_description = 'Username'
    user_display.admin_order_field = 'user__username'
    
    def is_active_badge(self, obj):
        color = '#4CAF50' if obj.is_active else '#F44336'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    is_active_badge.short_description = 'Active'
    is_active_badge.admin_order_field = 'is_active'
    
    def is_verified_badge(self, obj):
        color = '#4CAF50' if obj.is_verified else '#FFA500'
        text = 'Verified' if obj.is_verified else 'Unverified'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    is_verified_badge.short_description = 'Verified'
    is_verified_badge.admin_order_field = 'is_verified'
    
    def role_badge(self, obj):
        colors = {
            'CUSTOMER': '#2196F3',
            'AGENT': '#FF9800',
            'ADMIN': '#9C27B0'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.role, '#000000'),
            obj.role
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def last_login_display(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M') if obj.last_login else 'Never'
    last_login_display.short_description = 'Last Login'
    last_login_display.admin_order_field = 'last_login'
    
    def account_summary(self, obj):
        customer_exists = hasattr(obj, 'customer')
        total_loans = obj.customer.loan_set.count() if customer_exists else 0
        
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Has Customer Profile:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Total Loans:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Last Login:</strong></td><td>{}</td></tr>'
            '</table>',
            'Yes' if customer_exists else 'No',
            total_loans,
            obj.last_login.strftime('%Y-%m-%d %H:%M') if obj.last_login else 'Never'
        )
    account_summary.short_description = 'Account Summary'
    
    # Admin actions
    def activate_accounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} accounts activated.')
    activate_accounts.short_description = 'Activate accounts'
    
    def deactivate_accounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} accounts deactivated.')
    deactivate_accounts.short_description = 'Deactivate accounts'
    
    def verify_accounts(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} accounts verified.')
    verify_accounts.short_description = 'Verify accounts'
    
    def reset_verification(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} accounts unverified.')
    reset_verification.short_description = 'Reset verification'
