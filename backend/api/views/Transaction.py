from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models.Transaction import Transaction
from ..serializers.Transaction import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    search_fields = ['customer__first_name', 'customer__last_name', 'reference_number', 'transaction_type']
    ordering_fields = ['created_at', 'amount']
    filterset_fields = ['transaction_type', 'loan', 'customer']

    def get_queryset(self):
        """
        Enhanced queryset with filtering
        """
        queryset = super().get_queryset()
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by loan
        loan_id = self.request.query_params.get('loan_id', None)
        if loan_id:
            queryset = queryset.filter(loan_id=loan_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent transactions
        """
        recent_transactions = self.get_queryset()[:20]
        serializer = self.get_serializer(recent_transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get transactions grouped by customer
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transactions = self.get_queryset().filter(customer_id=customer_id)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
