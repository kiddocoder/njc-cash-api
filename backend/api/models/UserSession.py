from django.db import models

class UserSession(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='sessions')
    
    session_key = models.CharField(max_length=255, unique=True)
    
    # Device Information
    device_name = models.CharField(max_length=255, null=True, blank=True, help_text="Samsung Galaxy A13")
    device_type = models.CharField(max_length=50, null=True, blank=True, help_text="mobile, desktop, tablet")
    os_name = models.CharField(max_length=100, null=True, blank=True, help_text="Android, Windows, iOS")
    os_version = models.CharField(max_length=50, null=True, blank=True)
    browser_name = models.CharField(max_length=100, null=True, blank=True, help_text="Chrome, Safari, Firefox")
    browser_version = models.CharField(max_length=50, null=True, blank=True)
    
    # Location
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    
    # Session metadata
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.device_name or self.browser_name} - {self.user.username}"
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
