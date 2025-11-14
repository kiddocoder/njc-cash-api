from django.contrib import admin
from django.utils.html import format_html
from api.models.Notification import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_display',
        'notification_type_badge',
        'title_display',
        'is_read_badge',
        'created_at'
    ]
    
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'user__username',
        'title',
        'message',
        'id'
    ]
    
    readonly_fields = ['created_at', 'read_at', 'metadata_display']
    
    fieldsets = (
        ('Notification Details', {
            'fields': (
                'user',
                'notification_type',
                'title',
                'message',
                'related_loan',
                'related_payment'
            )
        }),
        ('Status', {
            'fields': (
                'is_read',
                'read_at'
            )
        }),
        ('Additional Data', {
            'fields': (
                'metadata',
                'metadata_display',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_notifications']
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def user_display(self, obj):
        return obj.user.username
    user_display.short_description = 'User'
    
    def notification_type_badge(self, obj):
        colors = {
            'LOAN_REQUEST': '#2196F3',
            'LOAN_APPROVAL': '#4CAF50',
            'LOAN_REJECTION': '#F44336',
            'PAYMENT_DUE': '#FFA500',
            'PAYMENT_RECEIVED': '#4CAF50',
            'MESSAGE': '#9C27B0',
            'SYSTEM': '#607D8B'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.notification_type, '#000000'),
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'
    
    def title_display(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_display.short_description = 'Title'
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #4CAF50;">✓ Read</span>')
        return format_html('<span style="color: #FFA500;">● Unread</span>')
    is_read_badge.short_description = 'Status'
    
    def metadata_display(self, obj):
        if obj.metadata:
            return format_html('<pre>{}</pre>', str(obj.metadata))
        return 'No metadata'
    metadata_display.short_description = 'Metadata'
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'
    
    def delete_notifications(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} notifications deleted.')
    delete_notifications.short_description = 'Delete notifications'
