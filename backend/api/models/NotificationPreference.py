from django.db import models

class NotificationPreference(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email Notifications
    new_loan_application_email = models.BooleanField(default=True)
    document_verification_email = models.BooleanField(default=True)
    pending_approval_email = models.BooleanField(default=True)
    client_messages_email = models.BooleanField(default=True)
    payment_processing_email = models.BooleanField(default=True)
    system_updates_email = models.BooleanField(default=True)
    
    # Push Notifications
    new_loan_application_push = models.BooleanField(default=True)
    document_verification_push = models.BooleanField(default=True)
    pending_approval_push = models.BooleanField(default=True)
    client_messages_push = models.BooleanField(default=True)
    payment_processing_push = models.BooleanField(default=True)
    system_updates_push = models.BooleanField(default=True)
    
    # SMS Notifications
    payment_due_sms = models.BooleanField(default=True)
    loan_status_sms = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
