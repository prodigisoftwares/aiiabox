from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.chats.models import Chat


class ChatListView(LoginRequiredMixin, ListView):
    """
    View for listing user's chats with pagination.

    Displays all chats owned by the authenticated user, ordered by most recently
    updated first. Paginates results (20 per page) for performance.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)

    Context:
        - chat_list: Paginated QuerySet of user's chats
        - paginator: Pagination object
        - page_obj: Current page object
        - is_paginated: Boolean indicating if results are paginated

    Returns:
        - GET: Rendered chat list page with paginated chats
    """

    model = Chat
    template_name = "chats/chat_list.html"
    context_object_name = "chats"
    paginate_by = 20

    def get_queryset(self):
        """
        Get chats for the current user only.

        Filters queryset to return only chats belonging to the authenticated user.
        Already ordered by -updated_at via model Meta.ordering.

        Returns:
            QuerySet: Chats belonging to current user, ordered by most recent first
        """
        return Chat.objects.filter(user=self.request.user)
