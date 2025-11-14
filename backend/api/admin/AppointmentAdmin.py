from django.contrib import admin
from django.utils.html import format_html
from api.models.Appointment import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_name',
        'description_short',
        'scheduled_time_display',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'scheduled_time',
        'created_at',
        ('customer', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'description',
        'id'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': (
                'customer',
                'description',
                'scheduled_time',
                'status'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_completed',
        'mark_cancelled',
        'reschedule_appointments'
    ]
    
    date_hierarchy = 'scheduled_time'
    ordering = ['-scheduled_time']
    list_per_page = 50
    
    # Custom display methods
    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
    
    def scheduled_time_display(self, obj):
        return obj.scheduled_time.strftime('%Y-%m-%d %H:%M')
    scheduled_time_display.short_description = 'Scheduled Time'
    scheduled_time_display.admin_order_field = 'scheduled_time'
    
    def status_badge(self, obj):
        colors = {
            'SCHEDULED': '#2196F3',
            'COMPLETED': '#4CAF50',
            'CANCELLED': '#F44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    # Admin actions
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} appointments marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} appointments cancelled.')
    mark_cancelled.short_description = 'Cancel appointments'
    
    def reschedule_appointments(self, request, queryset):
        self.message_user(request, f'Rescheduling {queryset.count()} appointments.')
    reschedule_appointments.short_description = 'Reschedule appointments'
