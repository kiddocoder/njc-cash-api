from django.contrib import admin
from api.models.Loan import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'status', 'created_at')
    ordering = ('-created_at',)