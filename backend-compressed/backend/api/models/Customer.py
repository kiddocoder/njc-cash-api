from django.db import models


class Customer(models.Model):

        account = models.OneToOneField(
            'Account',
            on_delete=models.CASCADE,
            related_name='customer'
        )

        profile_selfie = models.ImageField(upload_to='profile_selfies/', null=True, blank=True)
        national_id_front = models.ImageField(upload_to='national_id_fronts/', null=True, blank=True)
        national_id_back = models.ImageField(upload_to='national_id_backs/', null=True, blank=True)
        proof_of_address = models.ImageField(upload_to='proof_of_addresses/', null=True, blank=True)

       
        #Personal details
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)
        country = models.CharField(max_length=50)
        city = models.CharField(max_length=50)
        state = models.CharField(max_length=50)
        postal_code = models.CharField(max_length=20)
        address = models.TextField() # full address

        #Additional information
        gender = models.CharField(max_length=10, null=True, blank=True)
        date_of_birth = models.DateField(null=True, blank=True)
        place_of_birth = models.CharField(max_length=100, null=True, blank=True)
        education_degree = models.CharField(max_length=100, null=True, blank=True)
        job_status = models.CharField(max_length=100, null=True, blank=True)
        material_status = models.Choices(
            'MaterialStatus',
            'MARRIED SINGLE DIVORCED WIDOWED'
        )
        salary_range = models.CharField(max_length=50, null=True, blank=True)

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"{self.first_name} {self.last_name}"
        
        class Meta:
            verbose_name = 'Customer'
            verbose_name_plural = 'Customers'
            db_table = 'customers'