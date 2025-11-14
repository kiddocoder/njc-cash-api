from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models.Account import Account
from ..serializers.Account import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('-created_at')
    serializer_class = AccountSerializer
    search_fields = ['user__username', 'user__email', 'account_number']
    ordering_fields = ['created_at', 'user__username']
    filterset_fields = ['status', 'kyc_status', 'account_type']

    def get_queryset(self):
        """
        Enhanced queryset with filtering
        """
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by KYC status
        kyc_status = self.request.query_params.get('kyc_status', None)
        if kyc_status:
            queryset = queryset.filter(kyc_status=kyc_status)
        
        # Filter by account type
        account_type = self.request.query_params.get('account_type', None)
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(account_number__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['post'])
    def verify_kyc(self, request, pk=None):
        """
        Verify KYC for an account
        """
        account = self.get_object()
        account.kyc_status = 'VERIFIED'
        account.save()
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject_kyc(self, request, pk=None):
        """
        Reject KYC for an account
        """
        account = self.get_object()
        account.kyc_status = 'REJECTED'
        account.save()
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend an account
        """
        account = self.get_object()
        account.status = 'SUSPENDED'
        account.save()
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate an account
        """
        account = self.get_object()
        account.status = 'ACTIVE'
        account.save()
        serializer = self.get_serializer(account)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """
        Delete all accounts (for testing)
        """
        Account.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
