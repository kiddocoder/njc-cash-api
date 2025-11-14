from django.db import models


class EwalletPayment(models.Model):
    """
    Handles Ewallet disbursements (alternative to bank account transfers)
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PROVIDER_CHOICES = [
        ('MTN_MOBILE_MONEY', 'MTN Mobile Money'),
        ('VODACOM', 'Vodacom'),
        ('AIRTEL_MONEY', 'Airtel Money'),
        ('TELKOM', 'Telkom'),
        ('CAPITEC_PAY', 'Capitec Pay'),
    ]
    
    # Relationships
    loan = models.ForeignKey(
        'Loan',
        on_delete=models.CASCADE,
        related_name='ewallet_payments'
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='ewallet_payments'
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    # Ewallet details
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=200)
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Provider response
    provider_transaction_id = models.CharField(max_length=100, blank=True)
    provider_reference = models.CharField(max_length=100, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Audit
    initiated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_ewallet_payments'
    )
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ewallet Payment'
        verbose_name_plural = 'Ewallet Payments'
        db_table = 'ewallet_payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ewallet: {self.phone_number} - R{self.amount} ({self.status})"
