from django.contrib import admin
from django.utils.html import format_html
from api.models.KYCDocument import KYCDocument


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'document_type_display',
        'document_number',
        'status_badge',
        'verified_badge',
        'expiry_date',
        'verified_by_name',
        'document_preview'
    ]
    list_filter = [
        'document_type',
        'status',
        'is_verified',
        'expiry_date',
        'created_at'
    ]
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'document_number',
        'notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'verified_at',
        'verified_by',
        'document_image_preview'
    ]
    fieldsets = (
        ('Document Information', {
            'fields': ('customer', 'document_type', 'document_number', 'expiry_date')
        }),
        ('Document File', {
            'fields': ('document_image', 'document_image_preview')
        }),
        ('Verification', {
            'fields': ('status', 'is_verified', 'verified_at', 'verified_by', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_documents', 'reject_documents', 'mark_as_pending']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'customer__first_name'

    def document_type_display(self, obj):
        return obj.get_document_type_display()
    document_type_display.short_description = 'Type'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'expired': '#6c757d'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'

    def verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #dc3545;">✗ Not Verified</span>')
    verified_badge.short_description = 'Verified'

    def verified_by_name(self, obj):
        if obj.verified_by:
            return obj.verified_by.get_full_name() or obj.verified_by.username
        return '-'
    verified_by_name.short_description = 'Verified By'

    def document_preview(self, obj):
        if obj.document_image:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document_image.url)
        return '-'
    document_preview.short_description = 'Document'

    def document_image_preview(self, obj):
        if obj.document_image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;" />', obj.document_image.url)
        return 'No image uploaded'
    document_image_preview.short_description = 'Document Preview'

    def approve_documents(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            status='approved',
            is_verified=True,
            verified_at=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f'{count} document(s) approved.')
    approve_documents.short_description = 'Approve selected documents'

    def reject_documents(self, request, queryset):
        count = queryset.update(status='rejected', is_verified=False)
        self.message_user(request, f'{count} document(s) rejected.')
    reject_documents.short_description = 'Reject selected documents'

    def mark_as_pending(self, request, queryset):
        count = queryset.update(status='pending', is_verified=False)
        self.message_user(request, f'{count} document(s) marked as pending.')
    mark_as_pending.short_description = 'Mark as pending review'
