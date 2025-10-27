from rest_framework import viewsets
from ..models.Conversation import Conversation
from ..serializers.Conversation import ConversationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    search_fields = ['title', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'title']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Conversation.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)