from django.contrib import admin
from django.utils.html import format_html
from api.models.PaymentMethod import PaymentMethod

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_name',
        'payment_type_badge',
        'masked_details',
        'is_default_badge',
        'created_at'
    ]
    
    list_filter = [
        'payment_type',
        'is_default',
        'created_at',
        ('customer', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'customer__first_name',
        'customer__last_name',
        'card_last_four',
        'bank_name',
        'mobile_number'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer', {
            'fields': ('customer',)
        }),
        ('Payment Type', {
            'fields': ('payment_type', 'is_default')
        }),
        ('Card Details', {
            'fields': (
                'card_last_four',
                'card_expiry',
                'card_brand'
            ),
            'classes': ('collapse',)
        }),
        ('Bank Details', {
            'fields': (
                'bank_name',
                'account_number',
                'branch_code'
            ),
            'classes': ('collapse',)
        }),
        ('Mobile Money', {
            'fields': (
                'mobile_provider',
                'mobile_number'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['set_as_default', 'remove_payment_methods']
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    
    def payment_type_badge(self, obj):
        colors = {
            'CARD': '#2196F3',
            'BANK': '#4CAF50',
            'MOBILE_MONEY': '#FF9800'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_type, '#000000'),
            obj.get_payment_type_display()
        )
    payment_type_badge.short_description = 'Type'
    
    def masked_details(self, obj):
        if obj.payment_type == 'CARD':
            return f"**** **** **** {obj.card_last_four}"
        elif obj.payment_type == 'BANK':
            return f"{obj.bank_name} - ****{obj.account_number[-4:]}" if obj.account_number else obj.bank_name
        elif obj.payment_type == 'MOBILE_MONEY':
            return f"{obj.mobile_provider} - {obj.mobile_number}"
        return 'N/A'
    masked_details.short_description = 'Details'
    
    def is_default_badge(self, obj):
        if obj.is_default:
            return format_html('<span style="color: #4CAF50; font-weight: bold;">★ Default</span>')
        return ''
    is_default_badge.short_description = 'Default'
    
    def set_as_default(self, request, queryset):
        for payment_method in queryset:
            # Remove default from other methods
            PaymentMethod.objects.filter(customer=payment_method.customer).update(is_default=False)
            payment_method.is_default = True
            payment_method.save()
        self.message_user(request, f'{queryset.count()} payment methods set as default.')
    set_as_default.short_description = 'Set as default'
    
    def remove_payment_methods(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} payment methods removed.')
    remove_payment_methods.short_description = 'Remove payment methods'
