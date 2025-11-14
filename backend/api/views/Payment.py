from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
import uuid
from ..models.Payment import Payment
from ..models.Loan import Loan
from ..serializers.Payment import PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    filterset_fields = ['loan', 'customer', 'status', 'payment_type']
    
    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """Process a loan payment"""
        loan_id = request.data.get('loan_id')
        amount = request.data.get('amount')
        payment_method_id = request.data.get('payment_method_id')
        payment_type = request.data.get('payment_type', 'REGULAR')
        
        try:
            loan = Loan.objects.get(id=loan_id)
            
            # Create payment record
            payment = Payment.objects.create(
                loan=loan,
                customer=loan.borrower,
                payment_method_id=payment_method_id,
                amount=Decimal(amount),
                payment_type=payment_type,
                status='PROCESSING',
                transaction_id=str(uuid.uuid4())
            )
            
            # Simulate payment processing
            # In production, integrate with payment gateway
            payment.status = 'COMPLETED'
            payment.processed_at = timezone.now()
            payment.save()
            
            # Update loan balance
            loan.remaining_balance -= Decimal(amount)
            if loan.remaining_balance <= 0:
                loan.remaining_balance = Decimal('0.00')
                loan.status = 'CLOSED'
            
            # Update repayment progress
            if loan.total_amount > 0:
                paid_amount = loan.total_amount - loan.remaining_balance
                loan.repayment_progress = int((paid_amount / loan.total_amount) * 100)
            
            loan.save()
            
            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Loan.DoesNotExist:
            return Response(
                {'error': 'Loan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def loan_payments(self, request):
        """Get all payments for a specific loan"""
        loan_id = request.query_params.get('loan_id')
        if not loan_id:
            return Response(
                {'error': 'loan_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.queryset.filter(loan_id=loan_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
