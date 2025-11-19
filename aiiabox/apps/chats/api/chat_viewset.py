"""
DRF ViewSet for Chat model.

Provides CRUD operations for chats via REST API endpoints.
Implements proper filtering, authentication, and permission checks.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from ..models import Chat
from .chat_serializer import ChatSerializer
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
