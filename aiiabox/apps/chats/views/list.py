from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
        - page_title: Title for the page header
        - page_description: Description text for the page header
        - action_url: URL for the create chat action
        - action_text: Text for the create chat button
        - empty_title: Title for empty state
        - empty_description: Description for empty state

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

    def get_context_data(self, **kwargs):
        """
        Add additional context for template partials.

        Provides context variables needed by the refactored template partials
        for page header, empty state, and action buttons.

        Returns:
            dict: Context dictionary with additional variables
        """
        context = super().get_context_data(**kwargs)

        # Page header context
        context["page_title"] = _("Chats")

        # Dynamic description based on pagination state
        if context.get("is_paginated"):
            chat_count = context["paginator"].count
            context["page_description"] = (
                _("{} chat").format(chat_count)
                if chat_count == 1
                else _("{} chats").format(chat_count)
            )
        else:
            chat_count = len(context["chats"])
            context["page_description"] = (
                _("{} chat").format(chat_count)
                if chat_count == 1
                else _("{} chats").format(chat_count)
            )

        # Action button context
        context["action_url"] = reverse("chats:chat_create")
        context["action_text"] = _("New Chat")

        # Empty state context
        context["empty_title"] = _("No chats yet")
        context["empty_description"] = _(
            "Start a conversation by creating your first chat."
        )

        return context
