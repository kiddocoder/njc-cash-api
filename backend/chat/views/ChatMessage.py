from rest_framework import viewsets
from chat.models.ChatMessage import ChatMessage
from chat.serializers.ChatMessage import ChatMessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from api.utils.websocket_utils import send_chat_message

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('-created_at')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['message_text', 'sender__first_name', 'sender__last_name']
    filterset_fields = ['conversation', 'sender', 'message_type', 'is_read', 'created_at']
    ordering_fields = ['created_at', 'sender__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        unread_only = self.request.query_params.get('unread_only', None)
        if unread_only == 'true':
            queryset = queryset.filter(is_read=False)
        
        message_type = self.request.query_params.get('message_type', None)
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        return queryset

    def perform_create(self, serializer):
        message = serializer.save()
        send_chat_message(
            conversation_id=str(message.conversation.id),
            message_data=ChatMessageSerializer(message).data
        )

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'})

    @action(detail=False, methods=['post'])
    def mark_multiple_as_read(self, request):
        message_ids = request.data.get('message_ids', [])
        ChatMessage.objects.filter(id__in=message_ids).update(is_read=True)
        return Response({'status': f'{len(message_ids)} messages marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        conversation_id = request.query_params.get('conversation', None)
        if conversation_id:
            count = ChatMessage.objects.filter(
                conversation_id=conversation_id,
                is_read=False
            ).exclude(sender=request.user).count()
        else:
            count = ChatMessage.objects.filter(
                is_read=False
            ).exclude(sender=request.user).count()
        
        return Response({'unread_count': count})

    @action(detail=False, methods=['get'])
    def search_messages(self, request):
        query = request.query_params.get('q', '')
        conversation_id = request.query_params.get('conversation', None)
        
        messages = ChatMessage.objects.filter(
            Q(message_text__icontains=query)
        )
        
        if conversation_id:
            messages = messages.filter(conversation_id=conversation_id)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        ChatMessage.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
