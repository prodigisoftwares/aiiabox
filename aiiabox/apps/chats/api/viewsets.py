"""
DRF ViewSets for Chat and Message models.

Provides CRUD operations for chats and messages via REST API endpoints.
Implements proper filtering, authentication, and permission checks.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from ..models import Chat, Message
from .chat_serializer import ChatSerializer
from .message_serializer import MessageSerializer
from .permissions import IsOwnerOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for list endpoints.

    Returns 20 items per page, allows customization via ?page_size=N
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Chat CRUD operations.

    Endpoints:
    - GET /api/chats/ - List user's chats (paginated, ordered by -updated_at)
    - POST /api/chats/ - Create new chat, auto-sets user from request
    - GET /api/chats/{id}/ - Retrieve single chat detail
    - PATCH /api/chats/{id}/ - Partial update of chat (title, etc.)
    - DELETE /api/chats/{id}/ - Delete chat (cascade deletes messages)

    Authentication: TokenAuthentication (requires 'Authorization: Token <token>')
    Permission: IsAuthenticated + IsOwnerOrReadOnly (users see only their chats)
    Pagination: 20 items per page on list endpoint

    Assumes: User is authenticated (enforced by IsAuthenticated permission)
    Filters: Queryset automatically filtered to current user's chats
    """

    serializer_class = ChatSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Filter chats to only those owned by current user.

        This is the critical security check - ensures users can never see
        or modify other users' chats via the API.
        """
        return Chat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create chat, auto-setting user to current authenticated user.

        Users cannot specify a different user in the request body - the user
        is always set from the authenticated request context.
        """
        serializer.save(user=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message CRUD operations (nested under Chat).

    Expected URL pattern: /api/chats/{chat_id}/messages/

    Endpoints:
    - GET /api/chats/{chat_id}/messages/ - List messages in chat (paginated)
    - POST /api/chats/{chat_id}/messages/ - Add message to chat
    - GET /api/chats/{chat_id}/messages/{id}/ - Retrieve single message
    - PATCH /api/chats/{chat_id}/messages/{id}/ - Update message (rarely used)
    - DELETE /api/chats/{chat_id}/messages/{id}/ - Delete message

    Authentication: TokenAuthentication (requires 'Authorization: Token <token>')
    Permission: IsAuthenticated + IsOwnerOrReadOnly (users access only their chats)
    Pagination: 20 items per page on list endpoint

    Assumes:
    - Chat exists and is owned by authenticated user
    - User is authenticated
    - Parent chat id is passed via URL kwarg: kwargs['parent_lookup_chat_id']

    Filters:
    - Queryset filtered to messages in specified chat
    - Chat must be owned by current user
    """

    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Filter messages to those in the specified chat owned by current user.

        Two levels of filtering:
        1. Chat must be in the chat_id URL parameter
        2. Chat must be owned by current user
        """
        # Nested router creates 'chat_pk' kwarg (not 'parent_lookup_chat_id')
        chat_id = self.kwargs.get("chat_pk")
        if not chat_id:  # pragma: no cover
            # Fallback for different routing patterns
            chat_id = self.kwargs.get("parent_lookup_chat_id")
        return Message.objects.filter(chat_id=chat_id, chat__user=self.request.user)

    def perform_create(self, serializer):
        """
        Create message, auto-setting user and chat.

        Both user and chat are auto-set from context (not from request body):
        - user: from authenticated request
        - chat: from URL parameter (chat_pk from nested router)

        This prevents users from creating messages in other users' chats.
        """
        chat_id = self.kwargs.get("chat_pk")
        if not chat_id:  # pragma: no cover
            chat_id = self.kwargs.get("parent_lookup_chat_id")
        chat = Chat.objects.get(id=chat_id, user=self.request.user)
        serializer.save(user=self.request.user, chat=chat)
