from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from ..models.Loan import Loan
from ..serializers.Loan import LoanSerializer, LoanDetailSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by('-created_at')
    serializer_class = LoanSerializer
    search_fields = ['borrower__first_name', 'borrower__last_name', 'status', 'loan_type']
    ordering_fields = ['created_at', 'amount', 'start_date', 'end_date']
    filterset_fields = ['status', 'loan_type']

    def get_queryset(self):
        """
        Enhanced queryset with filtering capabilities
        """
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by loan type
        loan_type = self.request.query_params.get('loan_type', None)
        if loan_type:
            queryset = queryset.filter(loan_type=loan_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        # Search by customer name or loan ID
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(borrower__first_name__icontains=search) |
                Q(borrower__last_name__icontains=search) |
                Q(id__icontains=search)
            )
        
        return queryset

    @action(detail=False, methods=['get'])
    def today_loans(self, request):
        """
        Get today's loans overview
        """
        today = datetime.now().date()
        loans = self.get_queryset().filter(created_at__date=today)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a loan
        """
        loan = self.get_object()
        loan.status = 'APPROVED'
        loan.save()
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a loan
        """
        loan = self.get_object()
        loan.status = 'REJECTED'
        loan.save()
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        """
        Disburse an approved loan
        """
        loan = self.get_object()
        if loan.status != 'APPROVED':
            return Response(
                {'error': 'Only approved loans can be disbursed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        loan.status = 'DISBURSED'
        loan.save()
        serializer = self.get_serializer(loan)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """
        Delete all loans (for testing)
        """
        Loan.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        """Get detailed loan information"""
        instance = self.get_object()
        serializer = LoanDetailSerializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def payoff(self, request, pk=None):
        """Pay off the entire loan"""
        loan = self.get_object()
        
        if loan.remaining_balance <= 0:
            return Response(
                {'error': 'Loan is already paid off'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # This would integrate with payment processing
        # For now, just mark as closed
        loan.remaining_balance = 0
        loan.repayment_progress = 100
        loan.status = 'CLOSED'
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
