from django.db import models

class KYCDocument(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=255)
    document_number = models.CharField(max_length=255)
    document_url = models.URLField()
    status = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_kyc_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_type

    class Meta:
        verbose_name = 'KYC Document'
        verbose_name_plural = 'KYC Documents'
        db_table = 'kyc_documents'