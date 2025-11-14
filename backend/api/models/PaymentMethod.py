from django.db import models

class PaymentMethod(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='payment_methods')
    
    PAYMENT_TYPE_CHOICES = [
        ('CARD', 'Card'),
        ('BANK_ACCOUNT', 'Bank Account'),
        ('MOBILE_MONEY', 'Mobile Money'),
    ]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='CARD')
    
    # For Cards
    card_type = models.CharField(max_length=50, null=True, blank=True, help_text="MasterCard, Visa, etc")
    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    card_expiry = models.CharField(max_length=7, null=True, blank=True, help_text="MM/YYYY")
    
    # For Bank Accounts
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    
    # For Mobile Money
    mobile_provider = models.CharField(max_length=50, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    date_hierarchy = 'created_at'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.payment_type == 'CARD':
            return f"{self.card_type} ****{self.card_last_four}"
        elif self.payment_type == 'BANK_ACCOUNT':
            return f"{self.bank_name} - {self.account_number}"
        else:
            return f"{self.mobile_provider} - {self.mobile_number}"
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
