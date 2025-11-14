from django.contrib import admin
from django.utils.html import format_html
from api.models.EwalletPayment import EwalletPayment


@admin.register(EwalletPayment)
class EwalletPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'customer_name',
        'amount_display',
        'provider_badge',
        'status_badge',
        'phone_number',
        'created_at'
    ]
    list_filter = [
        'provider',
        'status',
        'created_at'
    ]
    search_fields = [
        'transaction_id',
        'customer__first_name',
        'customer__last_name',
        'phone_number',
        'provider_reference'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'completed_at',
        'provider_reference',
        'provider_response'
    ]
    fieldsets = (
        ('Payment Information', {
            'fields': ('customer', 'loan', 'transaction_id', 'amount', 'currency')
        }),
        ('Provider Details', {
            'fields': ('provider', 'phone_number', 'provider_reference')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'provider_response')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_completed', 'mark_as_failed', 'retry_payment']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'

    def amount_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{} {}</span>',
            obj.currency, f'{obj.amount:,.2f}'
        )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def provider_badge(self, obj):
        colors = {
            'mpesa': '#28a745',
            'airtel_money': '#dc3545',
            'orange_money': '#fd7e14',
            'mtn_mobile_money': '#ffc107'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.provider, '#6c757d'),
            obj.get_provider_display()
        )
    provider_badge.short_description = 'Provider'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#007bff',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'

    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{count} payment(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'

    def mark_as_failed(self, request, queryset):
        count = queryset.update(status='failed')
        self.message_user(request, f'{count} payment(s) marked as failed.')
    mark_as_failed.short_description = 'Mark as failed'

    def retry_payment(self, request, queryset):
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} payment(s) reset for retry.')
    retry_payment.short_description = 'Retry payment'
