from django.contrib import admin
from django.utils.html import format_html
from api.models.UserSession import UserSession

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_display',
        'device_info_short',
        'ip_address',
        'is_active_badge',
        'last_activity_display',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'last_activity',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'user__username',
        'device_type',
        'browser',
        'ip_address',
        'session_key'
    ]
    
    readonly_fields = [
        'created_at',
        'last_activity',
        'session_key',
        'session_details'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Session Details', {
            'fields': (
                'session_key',
                'is_active',
                'last_activity'
            )
        }),
        ('Device Information', {
            'fields': (
                'device_type',
                'device_name',
                'browser',
                'os',
                'ip_address',
                'location'
            )
        }),
        ('Additional Info', {
            'fields': (
                'session_details',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['terminate_sessions', 'mark_as_active']
    
    date_hierarchy = 'last_activity'
    ordering = ['-last_activity']
    
    def user_display(self, obj):
        return obj.user.username
    user_display.short_description = 'User'
    
    def device_info_short(self, obj):
        return f"{obj.device_type} - {obj.browser}"
    device_info_short.short_description = 'Device'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: #999;">○ Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def last_activity_display(self, obj):
        return obj.last_activity.strftime('%Y-%m-%d %H:%M:%S')
    last_activity_display.short_description = 'Last Activity'
    
    def session_details(self, obj):
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Device:</strong></td><td>{} - {}</td></tr>'
            '<tr><td><strong>Browser:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>OS:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>IP Address:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Location:</strong></td><td>{}</td></tr>'
            '</table>',
            obj.device_type,
            obj.device_name or 'Unknown',
            obj.browser or 'Unknown',
            obj.os or 'Unknown',
            obj.ip_address or 'Unknown',
            obj.location or 'Unknown'
        )
    session_details.short_description = 'Session Details'
    
    def terminate_sessions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} sessions terminated.')
    terminate_sessions.short_description = 'Terminate sessions'
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} sessions marked as active.')
    mark_as_active.short_description = 'Mark as active'
