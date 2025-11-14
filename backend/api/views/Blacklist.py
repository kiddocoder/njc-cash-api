from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from api.models import Blacklist, CreditBureauCheck, DocumentVerification, AuditLog, BiometricData
from api.serializers.Blacklist import (
    BlacklistSerializer, CreditBureauCheckSerializer,
    DocumentVerificationSerializer, AuditLogSerializer, BiometricDataSerializer
)


class BlacklistViewSet(viewsets.ModelViewSet):
    queryset = Blacklist.objects.select_related('customer', 'blacklisted_by', 'removed_by').all()
    serializer_class = BlacklistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'severity', 'reason']
    search_fields = ['sa_id_number', 'customer__first_name', 'customer__last_name', 'description']
    ordering_fields = ['blacklisted_at', 'severity', 'amount_owed']
    ordering = ['-blacklisted_at']
    
    @action(detail=False, methods=['post'])
    def check_blacklist(self, request):
        """
        Check if an SA ID is blacklisted
        """
        sa_id = request.data.get('sa_id_number')
        if not sa_id:
            return Response(
                {'error': 'sa_id_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        blacklist = Blacklist.objects.filter(
            sa_id_number=sa_id,
            is_active=True
        ).first()
        
        if blacklist:
            return Response({
                'is_blacklisted': True,
                'severity': blacklist.severity,
                'reason': blacklist.get_reason_display(),
                'blacklisted_at': blacklist.blacklisted_at,
                'amount_owed': str(blacklist.amount_owed)
            })
        
        return Response({
            'is_blacklisted': False,
            'message': 'No blacklist record found'
        })
    
    @action(detail=True, methods=['post'])
    def remove_from_blacklist(self, request, pk=None):
        """
        Remove a customer from blacklist
        """
        blacklist = self.get_object()
        removal_reason = request.data.get('removal_reason', '')
        
        blacklist.is_active = False
        blacklist.removed_by = request.user
        blacklist.removed_at = timezone.now()
        blacklist.removal_reason = removal_reason
        blacklist.save()
        
        # Update customer status
        if blacklist.customer:
            blacklist.customer.is_blacklisted = False
            blacklist.customer.save()
        
        return Response({
            'message': 'Customer removed from blacklist',
            'data': BlacklistSerializer(blacklist).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get blacklist statistics
        """
        total = Blacklist.objects.filter(is_active=True).count()
        by_severity = {}
        for severity, _ in Blacklist.SEVERITY_CHOICES:
            count = Blacklist.objects.filter(is_active=True, severity=severity).count()
            by_severity[severity] = count
        
        by_reason = {}
        for reason, _ in Blacklist.REASON_CHOICES:
            count = Blacklist.objects.filter(is_active=True, reason=reason).count()
            by_reason[reason] = count
        
        return Response({
            'total_blacklisted': total,
            'by_severity': by_severity,
            'by_reason': by_reason
        })


class CreditBureauCheckViewSet(viewsets.ModelViewSet):
    queryset = CreditBureauCheck.objects.select_related('customer', 'requested_by').all()
    serializer_class = CreditBureauCheckSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'result', 'bureau_provider']
    search_fields = ['sa_id_number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'credit_score']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def perform_check(self, request):
        """
        Perform a new credit bureau check
        """
        sa_id = request.data.get('sa_id_number')
        customer_id = request.data.get('customer_id')
        
        if not sa_id:
            return Response(
                {'error': 'sa_id_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # In production, this would call actual bureau API
        # For now, create a mock check
        check = CreditBureauCheck.objects.create(
            sa_id_number=sa_id,
            customer_id=customer_id,
            bureau_provider='TransUnion',
            check_type='STANDARD',
            status='SUCCESS',
            result='GOOD',  # This would come from actual API
            credit_score=650,
            requested_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'message': 'Credit check performed',
            'data': CreditBureauCheckSerializer(check).data
        }, status=status.HTTP_201_CREATED)


class DocumentVerificationViewSet(viewsets.ModelViewSet):
    queryset = DocumentVerification.objects.select_related('customer', 'reviewed_by').all()
    serializer_class = DocumentVerificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type', 'is_live_capture']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__sa_id_number']
    ordering_fields = ['created_at', 'confidence_score']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def verify_document(self, request, pk=None):
        """
        Manually verify a document
        """
        document = self.get_object()
        
        document.status = 'VERIFIED'
        document.reviewed_by = request.user
        document.reviewed_at = timezone.now()
        document.review_notes = request.data.get('notes', '')
        document.save()
        
        return Response({
            'message': 'Document verified',
            'data': DocumentVerificationSerializer(document).data
        })
    
    @action(detail=True, methods=['post'])
    def reject_document(self, request, pk=None):
        """
        Reject a document
        """
        document = self.get_object()
        
        document.status = 'REJECTED'
        document.reviewed_by = request.user
        document.reviewed_at = timezone.now()
        document.review_notes = request.data.get('notes', 'Document rejected')
        document.save()
        
        return Response({
            'message': 'Document rejected',
            'data': DocumentVerificationSerializer(document).data
        })
    
    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """
        Get all documents pending manual review
        """
        pending = self.queryset.filter(status='REQUIRES_REVIEW')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for audit logs
    """
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action_type', 'user', 'success', 'device_type']
    search_fields = ['action_description', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        Get activity for a specific user
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.queryset.filter(user_id=user_id)[:50]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class BiometricDataViewSet(viewsets.ModelViewSet):
    queryset = BiometricData.objects.select_related('customer').all()
    serializer_class = BiometricDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['biometric_type', 'is_active', 'customer']
    ordering_fields = ['registered_at', 'last_used']
    ordering = ['-registered_at']
    
    @action(detail=False, methods=['post'])
    def verify_biometric(self, request):
        """
        Verify biometric data against stored hash
        """
        customer_id = request.data.get('customer_id')
        biometric_type = request.data.get('biometric_type')
        biometric_hash = request.data.get('biometric_hash')
        
        if not all([customer_id, biometric_type, biometric_hash]):
            return Response(
                {'error': 'customer_id, biometric_type, and biometric_hash are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stored = BiometricData.objects.filter(
            customer_id=customer_id,
            biometric_type=biometric_type,
            is_active=True
        ).first()
        
        if not stored:
            return Response({
                'verified': False,
                'message': 'No biometric data found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # In production, use secure comparison
        verified = stored.biometric_hash == biometric_hash
        
        if verified:
            stored.last_used = timezone.now()
            stored.save()
        
        return Response({
            'verified': verified,
            'message': 'Biometric verified' if verified else 'Biometric verification failed'
        })
