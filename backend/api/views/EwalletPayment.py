from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from api.models import EwalletPayment, Loan
from api.serializers.EwalletPayment import EwalletPaymentSerializer


class EwalletPaymentViewSet(viewsets.ModelViewSet):
    queryset = EwalletPayment.objects.select_related('loan', 'customer', 'initiated_by').all()
    serializer_class = EwalletPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'provider', 'customer', 'loan']
    search_fields = ['phone_number', 'recipient_name', 'provider_transaction_id']
    ordering_fields = ['initiated_at', 'amount']
    ordering = ['-initiated_at']
    
    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """
        Initiate a new ewallet payment for loan disbursement
        """
        loan_id = request.data.get('loan_id')
        provider = request.data.get('provider')
        phone_number = request.data.get('phone_number')
        recipient_name = request.data.get('recipient_name')
        
        if not all([loan_id, provider, phone_number]):
            return Response(
                {'error': 'loan_id, provider, and phone_number are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create ewallet payment
        payment = EwalletPayment.objects.create(
            loan=loan,
            customer=loan.customer,
            provider=provider,
            phone_number=phone_number,
            recipient_name=recipient_name or loan.customer.full_name,
            amount=loan.amount,
            status='PENDING',
            initiated_by=request.user
        )
        
        # In production, call actual ewallet provider API here
        # For now, mark as processing
        payment.status = 'PROCESSING'
        payment.provider_transaction_id = f"EW-{payment.id}-{timezone.now().timestamp()}"
        payment.save()
        
        return Response({
            'message': 'Ewallet payment initiated',
            'data': EwalletPaymentSerializer(payment).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        """
        Mark payment as completed (called by webhook or manual)
        """
        payment = self.get_object()
        
        payment.status = 'COMPLETED'
        payment.completed_at = timezone.now()
        payment.provider_response = request.data.get('provider_response', {})
        payment.save()
        
        # Update loan status
        payment.loan.status = 'DISBURSED'
        payment.loan.disbursement_date = timezone.now()
        payment.loan.save()
        
        return Response({
            'message': 'Payment completed successfully',
            'data': EwalletPaymentSerializer(payment).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """
        Mark payment as failed
        """
        payment = self.get_object()
        
        payment.status = 'FAILED'
        payment.failed_at = timezone.now()
        payment.failure_reason = request.data.get('failure_reason', 'Payment failed')
        payment.provider_response = request.data.get('provider_response', {})
        payment.save()
        
        return Response({
            'message': 'Payment marked as failed',
            'data': EwalletPaymentSerializer(payment).data
        })
