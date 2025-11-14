from django.contrib import admin
from django.utils.html import format_html
from api.models.Blacklist import Blacklist


@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'reason_display',
        'severity_badge',
        'blacklisted_at',
        'expires_at',
        'is_permanent_badge',
        'blacklisted_by',
        'status_badge'
    ]
    list_filter = [
        'reason',
        'severity',
        'is_permanent',
        'blacklisted_at',
        'expires_at',
        'created_at'
    ]
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'customer__phone_number',
        'customer__email',
        'customer__id_number',
        'reason',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'blacklisted_by',
        'blacklisted_at'
    ]
    fieldsets = (
        ('Blacklist Information', {
            'fields': ('customer', 'reason', 'severity', 'notes')
        }),
        ('Duration', {
            'fields': ('is_permanent', 'blacklisted_at', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_expired', 'extend_blacklist', 'remove_from_blacklist']
    date_hierarchy = 'blacklisted_at'
    ordering = ['-blacklisted_at']

    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'

    def reason_display(self, obj):
        return obj.get_reason_display()
    reason_display.short_description = 'Reason'

    def severity_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.severity, '#6c757d'),
            obj.get_severity_display().upper()
        )
    severity_badge.short_description = 'Severity'

    def is_permanent_badge(self, obj):
        if obj.is_permanent:
            return format_html('<span style="color: #dc3545; font-weight: bold;">PERMANENT</span>')
        return format_html('<span style="color: #28a745;">Temporary</span>')
    is_permanent_badge.short_description = 'Type'

    def created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return 'System'
    created_by_name.short_description = 'Created By'

    def status_badge(self, obj):
        from django.utils import timezone
        if obj.is_permanent:
            return format_html('<span style="color: #dc3545; font-weight: bold;">ACTIVE (PERMANENT)</span>')
        elif obj.expires_at and obj.expires_at > timezone.now():
            return format_html('<span style="color: #ffc107; font-weight: bold;">ACTIVE</span>')
        else:
            return format_html('<span style="color: #6c757d;">EXPIRED</span>')
    status_badge.short_description = 'Status'

    def mark_as_expired(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(expires_at=timezone.now())
        self.message_user(request, f'{count} blacklist(s) marked as expired.')
    mark_as_expired.short_description = 'Mark selected as expired'

    def extend_blacklist(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        for blacklist in queryset:
            if not blacklist.is_permanent:
                blacklist.expires_at = timezone.now() + timedelta(days=90)
                blacklist.save()
        self.message_user(request, f'{queryset.count()} blacklist(s) extended by 90 days.')
    extend_blacklist.short_description = 'Extend by 90 days'

    def remove_from_blacklist(self, request, queryset):
        count = queryset.delete()[0]
        self.message_user(request, f'{count} customer(s) removed from blacklist.')
    remove_from_blacklist.short_description = 'Remove from blacklist'
