from django.db import models
from decimal import Decimal

class Account(models.Model):

    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='account'
    )
    status = models.TextChoices(
        'AccountStatus',
        'ACTIVE INACTIVE SUSPENDED DELETED BANNED',
    )
    kyc_status = models.TextChoices(
        'KYCStatus',
        'PENDING VERIFIED REJECTED'
    )
    account_type=  models.TextChoices('AccountType', 'CITIZEN FOREIGNER BUSINESS') # Whether is CITIZEN,FOREIGNER,BUSINESS
    referal_citizen= models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True) #can be null if is a foreigner he should have a citizen id 
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_loans = models.BigIntegerField(default=0)
    account_number = models.CharField(max_length=20, unique=True)
    account_number = models.CharField(max_length=20, unique=True)

    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        db_table = 'accounts'