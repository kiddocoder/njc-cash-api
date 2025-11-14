from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.UserSession import UserSession
from ..serializers.UserSession import UserSessionSerializer

class UserSessionViewSet(viewsets.ModelViewSet):
    queryset = UserSession.objects.all().order_by('-last_activity')
    serializer_class = UserSessionSerializer
    filterset_fields = ['user', 'is_active']
    
    @action(detail=False, methods=['get'])
    def user_sessions(self, request):
        """Get all active sessions for a user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sessions = self.queryset.filter(user_id=user_id, is_active=True)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def logout_session(self, request, pk=None):
        """Logout a specific session"""
        session = self.get_object()
        session.is_active = False
        session.save()
        
        return Response({'message': 'Session logged out successfully'})
    
    @action(detail=False, methods=['post'])
    def logout_all_sessions(self, request):
        """Logout all sessions for a user"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        UserSession.objects.filter(user_id=user_id, is_active=True).update(is_active=False)
        
        return Response({'message': 'All sessions logged out successfully'})
