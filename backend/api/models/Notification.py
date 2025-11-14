from django.db import models

class Notification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
    
    NOTIFICATION_TYPE_CHOICES = [
        ('LOAN_REQUEST', 'Loan Request'),
        ('LOAN_APPROVED', 'Loan Approved'),
        ('LOAN_REJECTED', 'Loan Rejected'),
        ('PAYMENT_DUE', 'Payment Due'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('MESSAGE', 'Message'),
        ('REMINDER', 'Reminder'),
        ('SYSTEM_UPDATE', 'System Update'),
        ('DOCUMENT_REQUIRED', 'Document Required'),
    ]
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related objects
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, null=True, blank=True)
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE, null=True, blank=True)
    
    # Amount for financial notifications
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Action button
    action_text = models.CharField(max_length=50, null=True, blank=True, help_text="Text for action button")
    action_url = models.CharField(max_length=255, null=True, blank=True, help_text="URL or route for action")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.title}"
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
