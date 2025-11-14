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
    kyc_status = models.CharField(
         max_length=100,
         default="PENDING",
        choices=[
            ('PENDING', 'Pending'),
            ('VERIFIED', 'Verified'),
            ('REJECTED', 'Rejected'),
        ]
        
    )   
    account_type=  models.CharField(max_length=100, default="CITIZEN", choices=[
        ('CITIZEN', 'Citizen'),
        ('FOREIGNER', 'Foreigner'),
        ('BUSINESS', 'Business'),
    ]) # Whether is CITIZEN,FOREIGNER,BUSINESS
    role = models.CharField(max_length=100, default="CUSTOMER", choices=[
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
        ('AGENT', 'Agent'),
    ])
    referal_citizen= models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True) #can be null if is a foreigner he should have a citizen id 
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_loans = models.BigIntegerField(default=0)
    account_number = models.CharField(max_length=20, unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    otp_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
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
