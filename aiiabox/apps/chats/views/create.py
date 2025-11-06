from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.chats.forms import ChatForm
from apps.chats.models import Chat


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
