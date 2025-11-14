from django.db import models

class CreditCheck(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    bureau_name = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=255)
    credit_score = models.IntegerField()
    risk_level = models.CharField(max_length=255)
    check_status = models.CharField(max_length=255)
    bureau_response = models.TextField()
    notes = models.TextField()
    checked_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='checked_credit_checks')
    checked_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name}"

    class Meta:
        ordering = ['-checked_at']
        verbose_name = 'Credit Check'
        verbose_name_plural = 'Credit Checks'
        db_table = 'credit_checks'
