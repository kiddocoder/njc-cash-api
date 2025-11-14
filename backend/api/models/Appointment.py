from django.db import models

class Appointment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    description = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=50,
        default='SCHEDULED',
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pk 
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
