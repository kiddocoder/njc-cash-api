from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from chat.models.Conversation import Conversation

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'participants_count',
        'messages_count',
        'last_message_preview',
        'last_activity',
        'created_at'
    ]
    
    list_filter = [
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'title',
        'participants__username',
        'participants__email',
        'id'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'conversation_statistics']
    
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Conversation Details', {
            'fields': (
                'title',
                'participants',
                'last_message'
            )
        }),
        ('Statistics', {
            'fields': ('conversation_statistics',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['archive_conversations', 'clear_messages']
    
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']
    list_per_page = 50
    
    # Custom display methods
    def participants_count(self, obj):
        return format_html('<strong>{}</strong>', obj.participants.count())
    participants_count.short_description = 'Participants'
    
    def messages_count(self, obj):
        count = obj.messages.count()
        return format_html('<strong>{}</strong>', count)
    messages_count.short_description = 'Messages'
    
    def last_message_preview(self, obj):
        if obj.last_message:
            text = obj.last_message.text[:50] if obj.last_message.text else '[No text]'
            return format_html(
                '<span title="{}">{}</span>',
                obj.last_message.text,
                text + '...' if len(obj.last_message.text or '') > 50 else text
            )
        return 'No messages'
    last_message_preview.short_description = 'Last Message'
    
    def last_activity(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    last_activity.short_description = 'Last Activity'
    last_activity.admin_order_field = 'updated_at'
    
    def conversation_statistics(self, obj):
        total_messages = obj.messages.count()
        unread_messages = obj.messages.filter(delivery_status='SENT').count()
        participants = obj.participants.count()
        
        return format_html(
            '<table style="width:100%;">'
            '<tr><td><strong>Total Messages:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Unread Messages:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Participants:</strong></td><td>{}</td></tr>'
            '</table>',
            total_messages,
            unread_messages,
            participants
        )
    conversation_statistics.short_description = 'Statistics'
    
    # Admin actions
    def archive_conversations(self, request, queryset):
        self.message_user(request, f'{queryset.count()} conversations archived.')
    archive_conversations.short_description = 'Archive conversations'
    
    def clear_messages(self, request, queryset):
        total_deleted = 0
        for conversation in queryset:
            count = conversation.messages.count()
            conversation.messages.all().delete()
            total_deleted += count
        self.message_user(request, f'{total_deleted} messages cleared from {queryset.count()} conversations.')
    clear_messages.short_description = 'Clear all messages'
