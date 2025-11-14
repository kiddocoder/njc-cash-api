from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from datetime import date
from ..models.Repayment import Repayment
from ..serializers.Repayment import RepaymentSerializer

class RepaymentViewSet(viewsets.ModelViewSet):
    queryset = Repayment.objects.all().order_by('due_date')
    serializer_class = RepaymentSerializer
    search_fields = ['loan__borrower__first_name', 'loan__borrower__last_name', 'status']
    ordering_fields = ['due_date', 'amount_due', 'created_at']
    filterset_fields = ['status', 'loan']

    def get_queryset(self):
        """
        Enhanced queryset with filtering
        """
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by loan
        loan_id = self.request.query_params.get('loan_id', None)
        if loan_id:
            queryset = queryset.filter(loan_id=loan_id)
        
        # Filter overdue repayments
        show_overdue = self.request.query_params.get('overdue', None)
        if show_overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=date.today(),
                status='PENDING'
            )
        
        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming repayments (next 30 days)
        """
        from datetime import timedelta
        thirty_days_later = date.today() + timedelta(days=30)
        
        upcoming_repayments = self.get_queryset().filter(
            due_date__lte=thirty_days_later,
            status='PENDING'
        )
        
        serializer = self.get_serializer(upcoming_repayments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue repayments
        """
        overdue_repayments = self.get_queryset().filter(
            due_date__lt=date.today(),
            status='PENDING'
        )
        
        serializer = self.get_serializer(overdue_repayments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark a repayment as paid
        """
        repayment = self.get_object()
        payment_date = request.data.get('payment_date', date.today())
        amount_paid = request.data.get('amount_paid', repayment.amount_due)
        payment_method = request.data.get('payment_method', None)
        
        repayment.amount_paid = amount_paid
        repayment.payment_date = payment_date
        repayment.payment_method = payment_method
        
        # Determine status based on payment date
        if payment_date <= repayment.due_date:
            repayment.status = 'ON_TIME'
        else:
            repayment.status = 'LATE'
        
        repayment.save()
        
        serializer = self.get_serializer(repayment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get repayment statistics
        """
        total_due = self.get_queryset().filter(
            status='PENDING'
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        
        total_paid = self.get_queryset().exclude(
            status='PENDING'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        overdue_count = self.get_queryset().filter(
            due_date__lt=date.today(),
            status='PENDING'
        ).count()
        
        on_time_count = self.get_queryset().filter(status='ON_TIME').count()
        late_count = self.get_queryset().filter(status='LATE').count()
        missed_count = self.get_queryset().filter(status='MISSED').count()
        
        return Response({
            'total_due': str(total_due),
            'total_paid': str(total_paid),
            'overdue_count': overdue_count,
            'on_time_count': on_time_count,
            'late_count': late_count,
            'missed_count': missed_count
        })
