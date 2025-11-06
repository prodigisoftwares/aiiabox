from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from apps.chats.models import Chat


class ChatDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a specific chat with all its messages.

    Shows chat title and full message history. Only allows users to view their own chats.
    Returns 404 if chat doesn't exist or belongs to another user.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - Chat exists and belongs to current user

    Context:
        - chat: The Chat object with related messages
        - messages: Chat's messages (via related_name)

    Returns:
        - GET: Rendered chat detail page with messages
    """

    model = Chat
    template_name = "chats/chat_detail.html"
    context_object_name = "chat"

    def get_queryset(self):
        """
        Get chats for the current user only.

        Restricts queryset to current user's chats. If user tries to access
        another user's chat, returns empty queryset -> 404.

        Returns:
            QuerySet: Chats belonging to current user
        """
        return Chat.objects.filter(user=self.request.user)
