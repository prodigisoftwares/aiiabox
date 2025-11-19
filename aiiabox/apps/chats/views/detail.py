from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView

from apps.chats.forms import MessageForm
from apps.chats.models import Chat


class ChatDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a specific chat with all its messages.

    Shows chat title and full message history. Only allows users to view their own chats.
    Handles both GET (display) and POST (message creation) requests.
    Returns 404 if chat doesn't exist or belongs to another user.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - Chat exists and belongs to current user

    Context:
        - chat: The Chat object with related messages
        - messages: Chat's messages (via related_name)
        - form: MessageForm instance for message input

    POST Parameters:
        - content: Message text (required, max 5000 chars)

    Returns:
        - GET: Rendered chat detail page with messages and form
        - POST (valid): Partial HTML of new message item
        - POST (invalid): Form with validation errors
    """

    model = Chat
    template_name = "chats/chat_detail.html"
    context_object_name = "chat"
    form_class = MessageForm

    def get_queryset(self):
        """
        Get chats for the current user only.

        Restricts queryset to current user's chats. If user tries to access
        another user's chat, returns empty queryset -> 404.

        Returns:
            QuerySet: Chats belonging to current user
        """
        return Chat.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add MessageForm to context for template rendering.

        Returns:
            dict: Context with chat and empty MessageForm
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle message creation via POST request.

        Creates a new message with role='user' and assigns current user.
        Returns partial HTML of message item on success, form with errors on failure.

        Validates:
            - Message content is not empty
            - User is authenticated (enforced by mixin)
            - Chat belongs to current user (enforced by get_object)

        Returns:
            HttpResponse: Rendered _message_item.html on success, form errors on failure
        """
        self.object = self.get_object()

        form = self.form_class(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = self.object
            message.user = request.user
            message.role = "user"
            message.save()

            # Return partial HTML of new message item
            return render(
                request,
                "chats/includes/_message_item.html",
                {"message": message},
            )

        # Form invalid - return full page with error feedback
        context = self.get_context_data(object=self.object)
        context["form"] = form
        return self.render_to_response(context)
