from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from apps.chats.models import Chat


class ChatDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a chat.

    Shows confirmation page before deletion. Only allows users to delete their own chats.
    Returns 404 if chat doesn't exist or belongs to another user.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - Chat exists and belongs to current user

    Returns:
        - GET: Rendered confirmation page
        - POST: Deletes chat and redirects to chat list
    """

    model = Chat
    template_name = "chats/chat_confirm_delete.html"
    success_url = reverse_lazy("chats:chat_list")

    def get_queryset(self):
        """
        Get chats for the current user only.

        Restricts queryset to current user's chats. If user tries to delete
        another user's chat, returns empty queryset -> 404.

        Returns:
            QuerySet: Chats belonging to current user
        """
        return Chat.objects.filter(user=self.request.user)
