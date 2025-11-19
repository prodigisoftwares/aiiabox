"""
Chat API module.

Provides REST API endpoints for chat CRUD operations with TokenAuthentication
and proper permission checks to ensure user isolation.
"""

from .permissions import IsOwnerOrReadOnly
from .serializers import ChatSerializer, MessageSerializer
from .viewsets import ChatViewSet, MessageViewSet

__all__ = [
    "IsOwnerOrReadOnly",
    "ChatSerializer",
    "MessageSerializer",
    "ChatViewSet",
    "MessageViewSet",
]
