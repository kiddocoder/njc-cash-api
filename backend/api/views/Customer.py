from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from django.utils import timezone
from ..models.Customer import Customer
from ..models.Loan import Loan
from ..serializers.Customer import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    search_fields = ['first_name', 'last_name', 'account__user__email']
    ordering_fields = ['created_at', 'first_name', 'last_name']

    def get_queryset(self):
        """
        Enhanced queryset with filtering
        """
        queryset = super().get_queryset()
        
        # Search by name, email, or phone
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(account__user__email__icontains=search)
            )
        
        # Filter by account status
        account_status = self.request.query_params.get('account_status', None)
        if account_status:
            queryset = queryset.filter(account__status=account_status)
        
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get customer statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        created_today = Customer.objects.filter(created_at__date=today).count()
        created_this_week = Customer.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        active_customers = Customer.objects.filter(
            account__status='ACTIVE'
        ).count()
        
        # Last week comparison
        last_week_created = Customer.objects.filter(
            created_at__date__gte=week_ago - timedelta(days=7),
            created_at__date__lt=week_ago
        ).count()
        
        percentage_change = 10.01  # Default
        if last_week_created > 0:
            percentage_change = ((created_this_week - last_week_created) / last_week_created) * 100
        
        return Response({
            'created_today': created_today,
            'created_this_week': created_this_week,
            'active_customers': active_customers,
            'percentage_change': round(percentage_change, 2)
        })

    @action(detail=True, methods=['get'])
    def loans(self, request, pk=None):
        """
        Get all loans for a specific customer
        """
        customer = self.get_object()
        loans = Loan.objects.filter(borrower=customer).order_by('-created_at')
        
        from ..serializers.Loan import LoanSerializer
        serializer = LoanSerializer(loans, many=True)
        
        # Calculate totals
        total_amount = loans.aggregate(total=Sum('amount'))['total'] or 0
        total_count = loans.count()
        
        return Response({
            'loans': serializer.data,
            'total_amount': str(total_amount),
            'total_count': total_count
        })
    
    @action(detail=True, methods=['get'])
    def recent_transactions(self, request, pk=None):
        """
        Get recent transactions for a customer
        """
        customer = self.get_object()
        recent_loans = Loan.objects.filter(
            borrower=customer
        ).order_by('-created_at')[:10]
        
        transactions = []
        for loan in recent_loans:
            transaction_type = 'Loan Request Submitted'
            if loan.status == 'APPROVED':
                transaction_type = 'Loan Request Approved'
            elif loan.status == 'REJECTED':
                transaction_type = 'Loan Request Rejected'
            elif loan.status == 'DISBURSED':
                transaction_type = 'Loan Disbursed'
            
            transactions.append({
                'id': loan.id,
                'type': transaction_type,
                'amount': str(loan.amount),
                'status': loan.status,
                'created_at': loan.created_at.isoformat(),
                'timestamp': loan.created_at.strftime('%I:%M %p')
            })
        
        return Response(transactions)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """
        Delete all customers (for testing)
        """
        Customer.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
