from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.Customer import CustomerViewSet
from api.views.Account import AccountViewSet
from api.views.ChatMessage import ChatMessageViewSet
from api.views.Conversation import ConversationViewSet
from api.views.Loan import LoanViewSet

router = DefaultRouter()

router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'chat-messages', ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
]
