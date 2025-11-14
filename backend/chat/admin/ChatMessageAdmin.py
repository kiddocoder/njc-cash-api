from django.contrib import admin
from django.utils.html import format_html
from chat.models.ChatMessage import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'sender_name',
        'conversation_title',
        'message_preview',
        'type_badge',
        'status_badge',
        'has_attachments',
        'created_at'
    ]
    
    list_filter = [
        'type',
        'delivery_status',
        'sync_status',
        'edited',
        'deleted',
        'created_at',
        ('conversation', admin.RelatedOnlyFieldListFilter),
        ('sender', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'text',
        'sender__username',
        'sender__email',
        'conversation__title',
        'id'
    ]
    
    readonly_fields = [
        'created_at',
        'edited_at',
        'message_details',
        'attachments_display',
        'reactions_display',
        'read_receipts_display'
    ]
    
    fieldsets = (
        ('Message Information', {
            'fields': (
                'conversation',
                'sender',
                'text',
                'type'
            )
        }),
        ('Attachments & Media', {
            'fields': (
                'attachments',
                'attachments_display'
            ),
            'classes': ('collapse',)
        }),
        ('Threading', {
            'fields': (
                'reply_to_message',
                'thread_id'
            ),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': (
                'reactions',
                'reactions_display',
                'read_receipts',
                'read_receipts_display'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Metadata', {
            'fields': (
                'delivery_status',
                'sync_status',
                'edited',
                'deleted',
                'metadata',
                'message_details',
                'created_at',
                'edited_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_read',
        'mark_as_delivered',
        'soft_delete_messages',
        'restore_messages'
    ]
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    
    # Custom display methods
    def sender_name(self, obj):
        return obj.sender.username
    sender_name.short_description = 'Sender'
    sender_name.admin_order_field = 'sender__username'
    
    def conversation_title(self, obj):
        return obj.conversation.title
    conversation_title.short_description = 'Conversation'
    conversation_title.admin_order_field = 'conversation__title'
    
    def message_preview(self, obj):
        if obj.deleted:
            return format_html('<em style="color: #999;">[Deleted]</em>')
        text = obj.text[:60] if obj.text else '[No text]'
        return text + '...' if len(obj.text or '') > 60 else text
    message_preview.short_description = 'Message'
    
    def type_badge(self, obj):
        colors = {
            'TEXT': '#2196F3',
            'IMAGE': '#4CAF50',
            'VIDEO': '#FF9800',
            'FILE': '#9C27B0'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.type, '#000000'),
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'
    type_badge.admin_order_field = 'type'
    
    def status_badge(self, obj):
        colors = {
            'SENT': '#FFA500',
            'DELIVERED': '#2196F3',
            'READ': '#4CAF50'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.delivery_status, '#000000'),
            obj.get_delivery_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'delivery_status'
    
    def has_attachments(self, obj):
        has_att = obj.attachments and len(obj.attachments) > 0
        return format_html(
            '<span style="color: {};">{}</span>',
            '#4CAF50' if has_att else '#999',
            '✓' if has_att else '✗'
        )
    has_attachments.short_description = 'Attachments'
    
    def message_details(self, obj):
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Edited:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Deleted:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Reactions:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Read by:</strong></td><td>{}</td></tr>'
            '</table>',
            'Yes' if obj.edited else 'No',
            'Yes' if obj.deleted else 'No',
            len(obj.reactions) if obj.reactions else 0,
            len(obj.read_receipts) if obj.read_receipts else 0
        )
    message_details.short_description = 'Details'
    
    def attachments_display(self, obj):
        if obj.attachments:
            return format_html('<pre>{}</pre>', str(obj.attachments))
        return 'No attachments'
    attachments_display.short_description = 'Attachments Data'
    
    def reactions_display(self, obj):
        if obj.reactions:
            return format_html('<pre>{}</pre>', str(obj.reactions))
        return 'No reactions'
    reactions_display.short_description = 'Reactions Data'
    
    def read_receipts_display(self, obj):
        if obj.read_receipts:
            return format_html('<pre>{}</pre>', str(obj.read_receipts))
        return 'No read receipts'
    read_receipts_display.short_description = 'Read Receipts Data'
    
    # Admin actions
    def mark_as_read(self, request, queryset):
        updated = queryset.update(delivery_status='READ')
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(delivery_status='DELIVERED')
        self.message_user(request, f'{updated} messages marked as delivered.')
    mark_as_delivered.short_description = 'Mark as delivered'
    
    def soft_delete_messages(self, request, queryset):
        updated = queryset.update(deleted=True)
        self.message_user(request, f'{updated} messages soft deleted.')
    soft_delete_messages.short_description = 'Soft delete messages'
    
    def restore_messages(self, request, queryset):
        updated = queryset.update(deleted=False)
        self.message_user(request, f'{updated} messages restored.')
    restore_messages.short_description = 'Restore deleted messages'
