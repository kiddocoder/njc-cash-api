from django.contrib import admin
from api.models.Loan import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount', 'status', 'created_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'status')
    ordering = ('-created_at',)