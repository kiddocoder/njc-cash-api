from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.NotificationPreference import NotificationPreference
from ..serializers.NotificationPreference import NotificationPreferenceSerializer

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    
    @action(detail=False, methods=['get'])
    def user_preferences(self, request):
        """Get notification preferences for a user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=400
            )
        
        preferences, created = NotificationPreference.objects.get_or_create(user_id=user_id)
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
