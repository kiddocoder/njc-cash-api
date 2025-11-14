from django.db import models
from decimal import Decimal

class Loan(models.Model):
    borrower = models.ForeignKey('Customer', on_delete=models.CASCADE)
    loan_type = models.CharField(
        max_length=100,
        default='PERSONAL',                       
        choices=[
          ('PERSONAL', 'Personal Loan'),
          ('MORTGAGE', 'Mortgage Loan'),
          ('AUTO', 'Auto Loan'),
          ('STUDENT', 'Student Loan'),
          ('BUSINESS', 'Business Loan')
           ]                           
         )
    repayment_methods = models.JSONField(default=dict, null=True, help_text="JSON field to store repayment methods")
    purpose_description = models.TextField(null=True, blank=True, help_text="Description of the loan purpose")
    billing_address = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    period_months = models.IntegerField(default=12, help_text="Loan period in months")
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total amount including interest")
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    repayment_progress = models.IntegerField(default=0, help_text="Repayment progress percentage")
    next_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    next_payment_date = models.DateField(null=True, blank=True)
    agreement_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=50,
        default='PENDING',
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('DISBURSED', 'Disbursed'),
            ('ACTIVE', 'Active'),
            ('CLOSED', 'Closed')
        ]
    )

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.pk} for {self.borrower}"
        
    def calculate_loan_details(self):
        """Calculate monthly payment, total amount, and other loan details"""
        if self.amount and self.interest_rate and self.period_months:
            # Simple interest calculation
            total_interest = (self.amount * self.interest_rate * self.period_months) / (100 * 12)
            self.total_amount = self.amount + total_interest
            self.monthly_payment = self.total_amount / self.period_months
            if not self.remaining_balance:
                self.remaining_balance = self.total_amount
            self.save()
    
    class Meta:
        db_table = 'loans'
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
