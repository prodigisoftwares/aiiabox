from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.chats.models import Chat
from apps.chats.views import ChatDetailView


class ChatDetailViewTests(TestCase):
    """Tests for ChatDetailView - focus on queryset filtering and authorization."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""
        cls.user1 = User.objects.create_user(
            username="testuser1", email="user1@test.com", password="testpass123"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", email="user2@test.com", password="testpass123"
        )

        cls.chat_user1 = Chat.objects.create(user=cls.user1, title="User 1 Chat")
        cls.chat_user2 = Chat.objects.create(user=cls.user2, title="User 2 Chat")

    def test_requires_authentication(self):
        """ChatDetailView requires authentication."""
        url = reverse("chats:chat_detail", kwargs={"pk": self.chat_user1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        expected_login_url = reverse("core:login")
        self.assertIn(expected_login_url, response.url)

    def test_queryset_filters_to_current_user(self):
        """get_queryset() returns only current user's chats."""
        view = ChatDetailView()
        view.request = type("Request", (), {"user": self.user1})()

        queryset = view.get_queryset()

        self.assertIn(self.chat_user1, queryset)
        self.assertNotIn(self.chat_user2, queryset)

    def test_404_when_accessing_other_user_chat(self):
        """User cannot access another user's chat (authorization)."""
        url = reverse("chats:chat_detail", kwargs={"pk": self.chat_user2.pk})
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_404_for_nonexistent_chat(self):
        """404 is returned for non-existent chat."""
        url = reverse("chats:chat_detail", kwargs={"pk": 99999})
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
