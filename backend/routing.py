from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add other protocols like "websocket" here
})
