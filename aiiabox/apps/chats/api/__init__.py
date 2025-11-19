"""
Chat API module.

Provides REST API endpoints for chat CRUD operations with TokenAuthentication
and proper permission checks to ensure user isolation.
"""

from .chat_serializer import ChatSerializer
from .message_serializer import MessageSerializer
from .permissions import IsOwnerOrReadOnly
from .viewsets import ChatViewSet, MessageViewSet

__all__ = [
    "IsOwnerOrReadOnly",
    "ChatSerializer",
    "MessageSerializer",
    "ChatViewSet",
    "MessageViewSet",
]
