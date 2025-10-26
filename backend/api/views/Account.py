# account view set

from rest_framework import viewsets
from ..models.Account import Account
from ..serializers.Account import AccountSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by('-created_at')
    serializer_class = AccountSerializer
    search_fields = ['username', 'email']
    ordering_fields = ['created_at', 'username']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Account.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)