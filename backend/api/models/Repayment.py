from django.db import models

class Repayment(models.Model):
    """
    Model to track loan repayment schedules and actual payments
    """
    REPAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('ON_TIME', 'Paid On Time'),
        ('LATE', 'Paid Late'),
        ('MISSED', 'Missed'),
    ]
    
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='repayments')
    
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=REPAYMENT_STATUS, default='PENDING')
    
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Repayment for Loan #{self.loan.id} - Due: {self.due_date}"
    
    class Meta:
        db_table = 'repayments'
        verbose_name = 'Repayment'
        verbose_name_plural = 'Repayments'
        ordering = ['due_date']
