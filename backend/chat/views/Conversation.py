from rest_framework import viewsets
from chat.models.Conversation import Conversation
from chat.serializers.Conversation import ConversationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import Q, Count, Max
from rest_framework.permissions import IsAuthenticated

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'customer__first_name', 'customer__last_name', 'customer__phone_number']
    filterset_fields = ['customer', 'is_active', 'created_at']
    ordering_fields = ['created_at', 'updated_at', 'title']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            message_count=Count('messages'),
            last_message_at=Max('messages__created_at')
        )
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'archived':
            queryset = queryset.filter(is_active=False)
        
        unread_only = self.request.query_params.get('unread_only', None)
        if unread_only == 'true':
            queryset = queryset.filter(messages__is_read=False).distinct()
        
        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conversation = self.get_object()
        conversation.messages.filter(is_read=False).update(is_read=True)
        return Response({'status': 'messages marked as read'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        conversation = self.get_object()
        conversation.is_active = False
        conversation.save()
        return Response({'status': 'conversation archived'})

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        conversation = self.get_object()
        conversation.is_active = True
        conversation.save()
        return Response({'status': 'conversation unarchived'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total = Conversation.objects.count()
        active = Conversation.objects.filter(is_active=True).count()
        archived = Conversation.objects.filter(is_active=False).count()
        with_unread = Conversation.objects.filter(messages__is_read=False).distinct().count()
        
        return Response({
            'total_conversations': total,
            'active_conversations': active,
            'archived_conversations': archived,
            'conversations_with_unread': with_unread
        })

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Conversation.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
