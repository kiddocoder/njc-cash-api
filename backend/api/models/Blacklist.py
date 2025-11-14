from django.db import models


class Blacklist(models.Model):
    """
    Tracks blacklisted customers based on SA ID or other identifiers.
    Integrates with credit bureau checks.
    """
    
    REASON_CHOICES = [
        ('DEFAULT', 'Loan Default'),
        ('FRAUD', 'Fraudulent Activity'),
        ('CREDIT_BUREAU', 'Credit Bureau Flag'),
        ('MANUAL', 'Manual Blacklist'),
        ('IDENTITY_THEFT', 'Identity Theft'),
        ('MULTIPLE_DEFAULTS', 'Multiple Defaults'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    # Identifiers
    sa_id_number = models.CharField(max_length=13, unique=True, db_index=True)
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blacklist_records'
    )
    
    # Blacklist details
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    description = models.TextField()
    amount_owed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Bureau information
    credit_bureau_source = models.CharField(max_length=100, blank=True)  # e.g., TransUnion, Experian
    bureau_reference_number = models.CharField(max_length=100, blank=True)
    bureau_check_date = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_permanent = models.BooleanField(default=False)
    blacklisted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='blacklisted_customers'
    )
    removed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='removed_blacklists'
    )
    removal_reason = models.TextField(blank=True)
    
    # Timestamps
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Blacklist Entry'
        verbose_name_plural = 'Blacklist Entries'
        db_table = 'blacklist'
        ordering = ['-blacklisted_at']
        indexes = [
            models.Index(fields=['sa_id_number', 'is_active']),
            models.Index(fields=['is_active', 'severity']),
        ]
    
    def __str__(self):
        return f"Blacklist: {self.sa_id_number} - {self.get_reason_display()}"


class CreditBureauCheck(models.Model):
    """
    Logs all credit bureau API calls for audit trail
    """
    
    CHECK_STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('TIMEOUT', 'Timeout'),
        ('ERROR', 'Error'),
    ]
    
    RESULT_CHOICES = [
        ('GOOD', 'Good Credit'),
        ('BAD', 'Bad Credit'),
        ('NO_RECORD', 'No Record Found'),
        ('ERROR', 'Error'),
    ]
    
    # Request details
    sa_id_number = models.CharField(max_length=13, db_index=True)
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bureau_checks'
    )
    
    # Check details
    bureau_provider = models.CharField(max_length=100)  # TransUnion, Experian, etc.
    check_type = models.CharField(max_length=50, default='STANDARD')
    status = models.CharField(max_length=20, choices=CHECK_STATUS_CHOICES)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    
    # Response data
    credit_score = models.IntegerField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, blank=True)
    has_defaults = models.BooleanField(default=False)
    default_count = models.IntegerField(default=0)
    total_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # API details
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    api_reference = models.CharField(max_length=100, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # Audit
    requested_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='bureau_checks_requested'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Credit Bureau Check'
        verbose_name_plural = 'Credit Bureau Checks'
        db_table = 'credit_bureau_checks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sa_id_number', 'created_at']),
            models.Index(fields=['result', 'created_at']),
        ]
    
    def __str__(self):
        return f"Bureau Check: {self.sa_id_number} - {self.get_result_display()}"


class DocumentVerification(models.Model):
    """
    Tracks document verification process with facial recognition and ID validation
    """
    
    DOCUMENT_TYPES = [
        ('PROFILE_PHOTO', 'Profile Photo'),
        ('SA_ID', 'SA ID Card'),
        ('BANK_STATEMENT', 'Bank Statement'),
        ('CREDIT_CARD', 'Credit Card'),
        ('PROOF_ADDRESS', 'Proof of Address'),
        ('AFFIDAVIT', 'Affidavit'),
        ('LIVE_SELFIE', 'Live Selfie'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
        ('REQUIRES_REVIEW', 'Requires Manual Review'),
    ]
    
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='document_verifications'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='documents/%Y/%m/%d/')
    
    # Verification details
    status = models.CharField(max_length=50, choices=VERIFICATION_STATUS, default='PENDING')
    verification_method = models.CharField(max_length=100, blank=True)  # FACIAL_RECOGNITION, OCR, MANUAL
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # 0-100
    
    # Facial recognition (for selfies vs profile photo)
    face_match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    face_detection_passed = models.BooleanField(null=True, blank=True)
    
    # OCR extracted data (for IDs, cards, statements)
    extracted_data = models.JSONField(default=dict, blank=True)
    ocr_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Manual review
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents'
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_live_capture = models.BooleanField(default=False)  # Photo taken live vs uploaded
    device_info = models.JSONField(default=dict, blank=True)
    location = models.JSONField(default=dict, blank=True)  # GPS coordinates
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Document Verification'
        verbose_name_plural = 'Document Verifications'
        db_table = 'document_verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'document_type', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.customer} ({self.status})"


class AuditLog(models.Model):
    """
    Comprehensive audit trail for all system actions
    """
    
    ACTION_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('ACCOUNT_CREATE', 'Account Created'),
        ('ACCOUNT_UPDATE', 'Account Updated'),
        ('ACCOUNT_DELETE', 'Account Deleted'),
        ('LOAN_REQUEST', 'Loan Requested'),
        ('LOAN_APPROVE', 'Loan Approved'),
        ('LOAN_REJECT', 'Loan Rejected'),
        ('LOAN_DISBURSE', 'Loan Disbursed'),
        ('PAYMENT_MADE', 'Payment Made'),
        ('BLACKLIST_ADD', 'Added to Blacklist'),
        ('BLACKLIST_REMOVE', 'Removed from Blacklist'),
        ('KYC_VERIFY', 'KYC Verified'),
        ('KYC_REJECT', 'KYC Rejected'),
        ('DOCUMENT_UPLOAD', 'Document Uploaded'),
        ('DOCUMENT_VERIFY', 'Document Verified'),
        ('BUREAU_CHECK', 'Credit Bureau Check'),
        ('SETTINGS_CHANGE', 'Settings Changed'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('ROLE_CHANGE', 'Role Changed'),
    ]
    
    # Who
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    user_role = models.CharField(max_length=50, blank=True)
    
    # What
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_description = models.TextField()
    
    # Where
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # MOBILE, DESKTOP, TABLET
    location = models.JSONField(default=dict, blank=True)
    
    # Context
    affected_model = models.CharField(max_length=100, blank=True)  # Customer, Loan, Account, etc.
    affected_object_id = models.IntegerField(null=True, blank=True)
    before_data = models.JSONField(default=dict, blank=True)
    after_data = models.JSONField(default=dict, blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['affected_model', 'affected_object_id']),
        ]
    
    def __str__(self):
        return f"{self.action_type} by {self.user} at {self.created_at}"


class BiometricData(models.Model):
    """
    Stores fingerprint and other biometric data securely
    """
    
    BIOMETRIC_TYPES = [
        ('FINGERPRINT', 'Fingerprint'),
        ('FACE', 'Face Recognition'),
        ('VOICE', 'Voice Recognition'),
    ]
    
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='biometric_data'
    )
    biometric_type = models.CharField(max_length=20, choices=BIOMETRIC_TYPES)
    
    # Encrypted biometric hash (never store raw data)
    biometric_hash = models.TextField()
    encoding_algorithm = models.CharField(max_length=50, default='SHA256')
    
    # Metadata
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    capture_device = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    registered_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_biometric_data'
    )
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        verbose_name = 'Biometric Data'
        verbose_name_plural = 'Biometric Data'
        db_table = 'biometric_data'
        unique_together = [['customer', 'biometric_type']]
    
    def __str__(self):
        return f"{self.customer} - {self.get_biometric_type_display()}"
