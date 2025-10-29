from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views.ChatMessage import ChatMessageViewSet
from chat.views.Conversation import ConversationViewSet

router = DefaultRouter()

router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'chat-messages', ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
]
