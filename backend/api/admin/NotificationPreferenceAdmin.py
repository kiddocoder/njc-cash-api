from django.contrib import admin
from api.models.NotificationPreference import NotificationPreference

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'document_verification_email',
        'pending_approval_email',
        'client_messages_email',
        'payment_processing_email',
        'system_updates_email',
        'new_loan_application_push',
        'document_verification_push',
        'pending_approval_push',
        'client_messages_push',
        'payment_processing_push',
        'system_updates_push',
        'payment_due_sms',
        'loan_status_sms'
    ]
    
    list_filter = [
        'document_verification_email',
        'pending_approval_email',
        'client_messages_email',
        'payment_processing_email',
        'system_updates_email',
        'new_loan_application_push',
        'document_verification_push',
        'pending_approval_push',
        'client_messages_push',
        'payment_processing_push',
        'system_updates_push',
        'payment_due_sms',
        'loan_status_sms'
    ]
    
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Types', {
            'fields': (
                'document_verification_email',
                'pending_approval_email',
                'client_messages_email',
                'payment_processing_email',
                'system_updates_email'
            )
        }),
        ('Push Notifications', {
            'fields': (
                'new_loan_application_push',
                'document_verification_push',
                'pending_approval_push',
                'client_messages_push',
                'payment_processing_push',
                'system_updates_push'
            )
        }),
        ('SMS Notifications', {
            'fields': (
                'payment_due_sms',
                'loan_status_sms'
            )
        }),
    )
    
    actions = ['enable_all_notifications', 'disable_all_notifications']
    
    def enable_all_notifications(self, request, queryset):
        queryset.update(
            document_verification_email=True,
            pending_approval_email=True,
            client_messages_email=True,
            payment_processing_email=True,
            system_updates_email=True,
            new_loan_application_push=True,
            document_verification_push=True,
            pending_approval_push=True,
            client_messages_push=True,
            payment_processing_push=True,
            system_updates_push=True,
            payment_due_sms=True,
            loan_status_sms=True
        )
        self.message_user(request, f'All notifications enabled for {queryset.count()} users.')
    enable_all_notifications.short_description = 'Enable all notifications'
    
    def disable_all_notifications(self, request, queryset):
        queryset.update(
            document_verification_email=False,
            pending_approval_email=False,
            client_messages_email=False,
            payment_processing_email=False,
            system_updates_email=False,
            new_loan_application_push=False,
            document_verification_push=False,
            pending_approval_push=False,
            client_messages_push=False,
            payment_processing_push=False,
            system_updates_push=False,
            payment_due_sms=False,
            loan_status_sms=False
        )
        self.message_user(request, f'All notifications disabled for {queryset.count()} users.')
    disable_all_notifications.short_description = 'Disable all notifications'

