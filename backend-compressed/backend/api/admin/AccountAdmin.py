# account admin

from django.contrib import admin
from api.models.Account import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    ordering = ('-created_at',)