from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.PaymentMethod import PaymentMethod
from ..serializers.PaymentMethod import PaymentMethodSerializer

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all().order_by('-created_at')
    serializer_class = PaymentMethodSerializer
    filterset_fields = ['customer', 'type', 'is_default', 'is_active']
    
    @action(detail=False, methods=['get'])
    def customer_methods(self, request):
        """Get all payment methods for a specific customer"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        methods = self.queryset.filter(customer_id=customer_id, is_active=True)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set a payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from other methods
        PaymentMethod.objects.filter(
            customer=payment_method.customer,
            is_default=True
        ).update(is_default=False)
        
        # Set this one as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)
