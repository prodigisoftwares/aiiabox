from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from apps.chats.forms import ChatForm
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


class ChatCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new chat.

    Displays form for user to enter chat title. On submission, creates a new Chat
    and assigns it to the authenticated user.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)

    Returns:
        - GET: Rendered chat creation form
        - POST (valid): Redirect to chat detail page of newly created chat
        - POST (invalid): Re-render form with validation errors

    Side effects:
        - Creates new Chat in database with current user as owner
    """

    model = Chat
    form_class = ChatForm
    template_name = "chats/chat_form.html"

    def form_valid(self, form):
        """
        Set the chat's user to the current user before saving.

        Overrides the form's save to automatically assign the chat to the
        authenticated user. This prevents users from creating chats for other users.

        Args:
            form: The validated ChatForm

        Returns:
            HttpResponse: Redirect response to chat detail page
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Get the URL to redirect to after successful chat creation.

        Returns URL for the newly created chat's detail page.

        Returns:
            str: URL path for chat detail view of newly created chat
        """
        return reverse_lazy("chats:chat_detail", kwargs={"pk": self.object.pk})


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
