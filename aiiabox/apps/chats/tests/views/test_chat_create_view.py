from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.chats.models import Chat
from apps.chats.views import ChatCreateView


class ChatCreateViewTests(TestCase):
    """Tests for ChatCreateView - focus on user assignment and form handling."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""
        cls.user = User.objects.create_user(
            username="testuser", email="user@test.com", password="testpass123"
        )

    def setUp(self):
        """Set up for each test."""
        self.url = reverse("chats:chat_create")

    def test_requires_authentication(self):
        """ChatCreateView requires authentication."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        expected_login_url = reverse("core:login")
        self.assertIn(expected_login_url, response.url)

    def test_uses_chatform(self):
        """ChatCreateView uses ChatForm."""
        from apps.chats.forms import ChatForm

        view = ChatCreateView()
        self.assertEqual(view.form_class, ChatForm)

    def test_creates_chat_with_valid_title(self):
        """ChatCreateView creates chat with valid title."""
        self.client.login(username="testuser", password="testpass123")
        data = {"title": "My New Chat"}

        # Should create chat
        self.client.post(self.url, data)

        chat = Chat.objects.get(title="My New Chat")
        self.assertEqual(chat.user, self.user)

    def test_user_auto_assigned_on_create(self):
        """Chat.user is automatically set to request.user in form_valid()."""
        self.client.login(username="testuser", password="testpass123")
        data = {"title": "New Chat"}

        self.client.post(self.url, data)

        chat = Chat.objects.get(title="New Chat")
        self.assertEqual(chat.user, self.user)

    def test_form_validation_empty_title(self):
        """Form validation rejects empty title."""
        from apps.chats.forms import ChatForm

        form = ChatForm(data={"title": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_validation_whitespace_trimming(self):
        """Form trims whitespace from title."""
        from apps.chats.forms import ChatForm

        form = ChatForm(data={"title": "  Chat Title  "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Chat Title")
