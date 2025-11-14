from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from api.consumers import ChatConsumer, NotificationConsumer, LoanUpdatesConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/loan-updates/$', LoanUpdatesConsumer.as_asgi()),
]
