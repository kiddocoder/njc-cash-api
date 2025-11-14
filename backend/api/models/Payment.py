from django.db import models
from decimal import Decimal

class Payment(models.Model):
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    PAYMENT_TYPE_CHOICES = [
        ('REGULAR', 'Regular Payment'),
        ('EARLY', 'Early Payment'),
        ('PAYOFF', 'Pay Off'),
    ]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='REGULAR')
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    transaction_reference = models.CharField(max_length=100, null=True, blank=True)
    
    notes = models.TextField(null=True, blank=True)


    payment_date = models.DateField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.pk} - R {self.amount} for Loan {self.loan.pk}"
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
