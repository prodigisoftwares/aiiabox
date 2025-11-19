"""
API URL routing for chat operations.

Registers viewsets with the DRF router and sets up nested message routing
under chats.
"""

from rest_framework_nested import routers

from .viewsets import ChatViewSet, MessageViewSet

# Main router for chat endpoints
router = routers.SimpleRouter()
router.register(r"chats", ChatViewSet, basename="chat")

# Nested router for messages under each chat
# Pattern: /api/chats/{chat_id}/messages/
messages_router = routers.NestedSimpleRouter(router, "chats", lookup="chat")
messages_router.register(r"messages", MessageViewSet, basename="message")

# Combine both routers' URL patterns
urlpatterns = router.urls + messages_router.urls
