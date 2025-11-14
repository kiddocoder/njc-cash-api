from django.contrib import admin
from django.utils.html import format_html
from api.models.Blacklist import BiometricData


@admin.register(BiometricData)
class BiometricDataAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'biometric_type_display',
        'is_verified_badge',
        'confidence_score_display',
        'registered_at',
        'device_info_short'
    ]
    list_filter = [
        'biometric_type',
        'is_verified',
        'registered_at'
    ]
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'device_info'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'registered_at',
        'biometric_image_preview'
    ]
    fieldsets = (
        ('Biometric Information', {
            'fields': ('customer', 'biometric_type', 'biometric_data', 'biometric_hash')
        }),
        ('Image', {
            'fields': ('biometric_image', 'biometric_image_preview')
        }),
        ('Verification', {
            'fields': ('is_verified', 'confidence_score', 'registered_at', 'device_info')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['verify_biometrics', 'revoke_verification']
    date_hierarchy = 'registered_at'
    ordering = ['-registered_at']

    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'

    def biometric_type_display(self, obj):
        return obj.get_biometric_type_display()
    biometric_type_display.short_description = 'Type'

    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #dc3545;">✗ Not Verified</span>')
    is_verified_badge.short_description = 'Verified'

    def confidence_score_display(self, obj):
        if obj.confidence_score:
            color = '#28a745' if obj.confidence_score >= 0.9 else '#ffc107' if obj.confidence_score >= 0.7 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color, int(obj.confidence_score * 100)
            )
        return '-'
    confidence_score_display.short_description = 'Confidence'

    def device_info_short(self, obj):
        if obj.device_info and len(obj.device_info) > 30:
            return obj.device_info[:30] + '...'
        return obj.device_info or '-'
    device_info_short.short_description = 'Device'

    def biometric_image_preview(self, obj):
        if obj.biometric_image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.biometric_image.url)
        return 'No image'
    biometric_image_preview.short_description = 'Biometric Preview'

    def verify_biometrics(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} biometric(s) verified.')
    verify_biometrics.short_description = 'Verify selected biometrics'

    def revoke_verification(self, request, queryset):
        count = queryset.update(is_verified=False)
        self.message_user(request, f'{count} biometric verification(s) revoked.')
    revoke_verification.short_description = 'Revoke verification'
