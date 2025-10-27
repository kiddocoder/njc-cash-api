from django.contrib import admin
from api.models.ChatMessage import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text', 'created_at')
    search_fields = ('message_text', 'sender__first_name', 'sender__last_name')
    ordering = ('-created_at',)
