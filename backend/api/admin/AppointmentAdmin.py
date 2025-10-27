from django.contrib import admin
from api.models.Appointment import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id',  'description', 'scheduled_time', 'status','created_at', 'updated_at')
    ordering = ('-scheduled_time',)