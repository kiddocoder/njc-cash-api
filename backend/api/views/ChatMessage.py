from rest_framework import viewsets
from ..models.ChatMessage import ChatMessage
from ..serializers.ChatMessage import ChatMessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('-created_at')
    serializer_class = ChatMessageSerializer
    search_fields = ['message_text', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['created_at', 'sender__first_name']

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        ChatMessage.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)