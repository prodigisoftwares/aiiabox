from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.chats.models import Chat
from apps.chats.views import ChatDeleteView


class ChatDeleteViewTests(TestCase):
    """Tests for ChatDeleteView - focus on authorization and deletion."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""
        cls.user1 = User.objects.create_user(
            username="testuser1", email="user1@test.com", password="testpass123"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", email="user2@test.com", password="testpass123"
        )

        cls.chat_user1 = Chat.objects.create(user=cls.user1, title="Delete Me")
        cls.chat_user2 = Chat.objects.create(user=cls.user2, title="Other Chat")

    def test_requires_authentication(self):
        """ChatDeleteView requires authentication."""
        url = reverse("chats:chat_delete", kwargs={"pk": self.chat_user1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        expected_login_url = reverse("core:login")
        self.assertIn(expected_login_url, response.url)

    def test_queryset_filters_to_current_user(self):
        """get_queryset() returns only current user's chats."""
        view = ChatDeleteView()
        view.request = type("Request", (), {"user": self.user1})()

        queryset = view.get_queryset()

        self.assertIn(self.chat_user1, queryset)
        self.assertNotIn(self.chat_user2, queryset)

    def test_404_when_accessing_other_user_chat(self):
        """User cannot delete another user's chat (authorization)."""
        url = reverse("chats:chat_delete", kwargs={"pk": self.chat_user2.pk})
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_deletes_correct_chat(self):
        """ChatDeleteView deletes only the specified chat."""
        # Create another chat for user1
        other_chat = Chat.objects.create(user=self.user1, title="Keep Me")

        url = reverse("chats:chat_delete", kwargs={"pk": self.chat_user1.pk})
        self.client.login(username="testuser1", password="testpass123")

        self.client.post(url)

        # Deleted chat should not exist
        self.assertFalse(Chat.objects.filter(pk=self.chat_user1.pk).exists())

        # Other chats should still exist
        self.assertTrue(Chat.objects.filter(pk=other_chat.pk).exists())
        self.assertTrue(Chat.objects.filter(pk=self.chat_user2.pk).exists())

    def test_success_url_is_chat_list(self):
        """success_url is set to chat_list."""
        view = ChatDeleteView()
        expected_url = reverse("chats:chat_list")
        self.assertEqual(view.success_url, expected_url)
