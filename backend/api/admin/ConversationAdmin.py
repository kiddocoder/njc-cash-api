from django.contrib import admin
from api.models.Conversation import Conversation

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)