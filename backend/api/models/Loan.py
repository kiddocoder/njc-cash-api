from django.db import models

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

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.pk} for {self.borrower}"