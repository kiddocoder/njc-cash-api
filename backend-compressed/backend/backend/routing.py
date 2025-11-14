from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from api.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'chat/', ChatConsumer.as_asgi()), # type: ignore
]
