from django.contrib import admin
from api.models.Customer import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('-created_at',)