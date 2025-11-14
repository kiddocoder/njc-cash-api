from django.db import models

class Transaction(models.Model):
    """
    Model to track all financial transactions including repayments, refunds, disbursements
    """
    TRANSACTION_TYPES = [
        ('LOAN_REQUEST', 'Loan Request Submitted'),
        ('LOAN_APPROVED', 'Loan Request Approved'),
        ('LOAN_REJECTED', 'Loan Request Rejected'),
        ('LOAN_DISBURSED', 'Loan Disbursed'),
        ('REPAYMENT', 'Loan Repayment'),
        ('REFUND', 'Loan Refund'),
        ('PENALTY', 'Late Payment Penalty'),
    ]
    
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='transactions')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # Bank transfer, cash, mobile money
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} for Loan #{self.loan.id}"
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
