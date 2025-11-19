"""
Chat API module.

Provides REST API endpoints for chat CRUD operations with TokenAuthentication
and proper permission checks to ensure user isolation.
"""

from .chat_serializer import ChatSerializer
from .chat_viewset import ChatViewSet
from .message_serializer import MessageSerializer
from .message_viewset import MessageViewSet
from .permissions import IsOwnerOrReadOnly

__all__ = [
    "IsOwnerOrReadOnly",
    "ChatSerializer",
    "MessageSerializer",
    "ChatViewSet",
    "MessageViewSet",
]
