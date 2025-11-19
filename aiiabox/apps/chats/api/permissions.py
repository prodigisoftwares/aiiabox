"""
API permission classes for chat operations.

Provides authorization checks to ensure users can only access/modify their own
chats and messages.
"""

from rest_framework import permissions

from ..models import Chat


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows full access to owners of a chat or message.

    Only the user who created a chat/message can view, edit, or delete it.
    This enforces user isolation - chats and messages are strictly private.

    Applies to:
    - Chat viewset: User can only see/modify their own chats
    - Message viewset: User can only see/modify their own messages in their chats
    """

    def has_permission(self, request, view):
        """
        Allow authenticated users to access API.

        For nested routes (messages), also verify the parent chat belongs to user.
        Actual object-level permission check happens in has_object_permission.
        """
        if not (request.user and request.user.is_authenticated):  # pragma: no cover
            return False

        # For nested message routes, verify parent chat belongs to user
        if "chat_pk" in view.kwargs:
            try:
                chat_id = view.kwargs["chat_pk"]
                # Check if chat exists and belongs to current user
                return Chat.objects.filter(id=chat_id, user=request.user).exists()
            except (ValueError, TypeError):  # pragma: no cover
                return False

        return True

    def has_object_permission(self, request, view, obj):  # pragma: no cover
        """
        Check if user owns the chat or message.

        For Chat: obj.user must match request.user
        For Message: obj.chat.user must match request.user
        """
        # Chat object
        if hasattr(obj, "messages"):  # Chat has 'messages' reverse relation
            return obj.user == request.user

        # Message object
        if hasattr(obj, "chat"):  # Message has 'chat' foreign key
            return obj.chat.user == request.user

        return False
