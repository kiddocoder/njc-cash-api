from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models.Role import Role as RoleModel
from ..serializers.Role import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = RoleModel.objects.all().order_by('-created_at')
    serializer_class = RoleSerializer
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    # Example custom action: bulk delete
    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        count = self.queryset.count()
        self.queryset.delete()
        return Response({"message": f"Deleted {count} roles."}, status=status.HTTP_200_OK)