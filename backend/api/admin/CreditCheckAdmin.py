from django.contrib import admin
from django.utils.html import format_html
from api.models.CreditCheck import CreditCheck

@admin.register(CreditCheck)
class CreditCheckAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'credit_score_display',
        'bureau_name',
        'check_status_badge',
        'risk_level_badge',
        'checked_at',
        'checked_by_name'
    ]
    list_filter = [
        'bureau_name',
        'check_status',
        'risk_level',
        'checked_at'
    ]
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'reference_number',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'checked_at',
        'checked_by'
    ]
    fieldsets = (
        ('Credit Check Information', {
            'fields': ('customer', 'bureau_name', 'reference_number')
        }),
        ('Credit Score', {
            'fields': ('credit_score', 'risk_level', 'check_status')
        }),
        ('Details', {
            'fields': ('bureau_response', 'notes')
        }),
        ('Metadata', {
            'fields': ('checked_by', 'checked_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['recheck_credit', 'mark_as_passed']
    date_hierarchy = 'checked_at'
    ordering = ['-checked_at']

    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'

    def credit_score_display(self, obj):
        if obj.credit_score:
            color = '#28a745' if obj.credit_score >= 700 else '#ffc107' if obj.credit_score >= 500 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold; font-size: 16px;">{}</span>',
                color, obj.credit_score
            )
        return '-'
    credit_score_display.short_description = 'Credit Score'

    def check_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.check_status, '#6c757d'),
            obj.get_check_status_display().upper()
        )
    check_status_badge.short_description = 'Status'

    def risk_level_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545'
        }
        if obj.risk_level:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
                colors.get(obj.risk_level, '#6c757d'),
                obj.get_risk_level_display().upper()
            )
        return '-'
    risk_level_badge.short_description = 'Risk Level'

    def checked_by_name(self, obj):
        if obj.checked_by:
            return obj.checked_by.get_full_name() or obj.checked_by.username
        return 'System'
    checked_by_name.short_description = 'Checked By'

    def recheck_credit(self, request, queryset):
        count = queryset.update(check_status='pending')
        self.message_user(request, f'{count} credit check(s) marked for rechecking.')
    recheck_credit.short_description = 'Recheck credit score'

    def mark_as_passed(self, request, queryset):
        count = queryset.update(check_status='completed', risk_level='low')
        self.message_user(request, f'{count} credit check(s) marked as passed.')
    mark_as_passed.short_description = 'Mark as passed'
