from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from apps.chats.forms import ChatForm
from apps.chats.models import Chat


class ChatCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new chat using a form.

    Displays a form for users to enter a chat title, then creates the chat
    and redirects to the chat detail page.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)

    Returns:
        - GET: Render form template
        - POST: Create chat and redirect to chat detail

    Side effects:
        - Creates new Chat in database with current user as owner
    """

    model = Chat
    form_class = ChatForm
    template_name = "chats/chat_form.html"
    success_url = reverse_lazy("chats:chat_list")

    def form_valid(self, form):
        """
        Handle valid form submission.

        Set the chat user to the current user and save the chat.
        """
        form.instance.user = self.request.user
        self.object = form.save()
        # Redirect to the newly created chat detail instead of list
        return redirect("chats:chat_detail", pk=self.object.pk)
