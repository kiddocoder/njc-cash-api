from django.db import models

class ChatMessage(models.Model):
    conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    MESSAGE_TYPE_CHOICES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('FILE', 'File'),
    ]
    type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='TEXT')
    text = models.TextField(null=True, blank=True)
    attachments = models.JSONField(default=list)  # List of attachment URLs or metadata
    reply_to_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    thread_id = models.CharField(max_length=255, null=True, blank=True)
    reactions = models.JSONField(default=list)  # List of reaction objects
    read_receipts = models.JSONField(default=list)  # List of read receipt objects
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    DELIVERY_STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
    ]
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUS_CHOICES, default='SENT')
    SYNC_STATUS_CHOICES = [
        ('SYNCED', 'Synced'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    ]
    sync_status = models.CharField(max_length=10, choices=SYNC_STATUS_CHOICES, default='SYNCED')
    metadata = models.JSONField(null=True, blank=True)  # Additional metadata

    def __str__(self):
        return f'Message {self.pk} in Conversation {self.conversation.id}'

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        db_table = 'chat_messages'