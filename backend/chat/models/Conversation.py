from django.db import models

class Conversation(models.Model):

    title = models.CharField(max_length=255)
    image_url = models.URLField(null=True, blank=True)
    participants = models.ManyToManyField(
        'auth.User',
        related_name='conversations'
    )
    admin_ids = models.JSONField(default=list)  # List of user IDs who are admins
    last_message = models.ForeignKey(
        'ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    muted = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)  # encryption, topic, etc.

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        db_table = 'conversations'