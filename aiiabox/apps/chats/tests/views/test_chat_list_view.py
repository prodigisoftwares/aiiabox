from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.chats.models import Chat
from apps.chats.views import ChatListView


class ChatListViewTests(TestCase):
    """Tests for ChatListView - focus on queryset filtering and authorization."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests in this class."""
        cls.user1 = User.objects.create_user(
            username="testuser1", email="user1@test.com", password="testpass123"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", email="user2@test.com", password="testpass123"
        )

        cls.chat1 = Chat.objects.create(user=cls.user1, title="Chat 1")
        cls.chat2 = Chat.objects.create(user=cls.user1, title="Chat 2")
        cls.chat3 = Chat.objects.create(user=cls.user1, title="Chat 3")
        cls.chat_other = Chat.objects.create(user=cls.user2, title="Other User Chat")

    def test_requires_authentication(self):
        """ChatListView requires authentication."""
        url = reverse("chats:chat_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        expected_login_url = reverse("core:login")
        self.assertIn(expected_login_url, response.url)

    def test_queryset_filters_to_current_user(self):
        """get_queryset() returns only current user's chats."""
        view = ChatListView()
        view.request = type("Request", (), {"user": self.user1})()

        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 3)
        self.assertIn(self.chat1, queryset)
        self.assertIn(self.chat2, queryset)
        self.assertIn(self.chat3, queryset)
        self.assertNotIn(self.chat_other, queryset)

    def test_queryset_empty_for_user_with_no_chats(self):
        """get_queryset() returns empty for user with no chats."""
        view = ChatListView()
        view.request = type("Request", (), {"user": self.user2})()

        # Remove other user's chat to test empty case
        Chat.objects.filter(user=self.user2).delete()
        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 0)

    def test_paginate_by_is_20(self):
        """paginate_by is set to 20 chats per page."""
        view = ChatListView()
        self.assertEqual(view.paginate_by, 20)

    def test_model_ordering_newest_first(self):
        """Chat model orders by -updated_at (newest first)."""
        chats = Chat.objects.filter(user=self.user1)
        chats_list = list(chats)

        # chat3 was created last, should be first
        self.assertEqual(chats_list[0].pk, self.chat3.pk)
