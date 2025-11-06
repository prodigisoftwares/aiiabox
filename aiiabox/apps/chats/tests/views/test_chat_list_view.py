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

    def test_get_context_data_with_chats(self):
        """get_context_data() provides correct context variables when user has chats."""
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("chats:chat_list"))

        self.assertEqual(response.status_code, 200)

        # Check page header context
        self.assertEqual(response.context["page_title"], "Chats")

        # Check action button context
        self.assertEqual(response.context["action_url"], reverse("chats:chat_create"))
        self.assertEqual(response.context["action_text"], "New Chat")

        # Check empty state context (should still be present even with chats)
        self.assertEqual(response.context["empty_title"], "No chats yet")
        self.assertEqual(
            response.context["empty_description"],
            "Start a conversation by creating your first chat.",
        )

        # Check page description for non-paginated case (3 chats < 20)
        self.assertEqual(response.context["page_description"], "3 chats")

    def test_get_context_data_with_no_chats(self):
        """get_context_data() provides correct context variables when user has no chats."""
        # Create a user with no chats
        User.objects.create_user(
            username="user_no_chats", email="nochats@test.com", password="testpass123"
        )

        self.client.login(username="user_no_chats", password="testpass123")
        response = self.client.get(reverse("chats:chat_list"))

        self.assertEqual(response.status_code, 200)

        # Check page description for empty case
        self.assertEqual(response.context["page_description"], "0 chats")

    def test_get_context_data_singular_chat_count(self):
        """get_context_data() uses singular form for single chat."""
        # Create a user with only one chat
        user_single_chat = User.objects.create_user(
            username="user_single", email="single@test.com", password="testpass123"
        )
        Chat.objects.create(user=user_single_chat, title="Single Chat")

        self.client.login(username="user_single", password="testpass123")
        response = self.client.get(reverse("chats:chat_list"))

        self.assertEqual(response.status_code, 200)

        # Check page description uses singular form
        self.assertEqual(response.context["page_description"], "1 chat")

    def test_get_context_data_with_paginated_chats(self):
        """get_context_data() provides correct context variables when chats are paginated."""
        # Create a user with more than 20 chats to trigger pagination
        user_many_chats = User.objects.create_user(
            username="user_many", email="many@test.com", password="testpass123"
        )

        # Create 25 chats (more than paginate_by=20)
        for i in range(25):
            Chat.objects.create(user=user_many_chats, title=f"Chat {i+1}")

        self.client.login(username="user_many", password="testpass123")
        response = self.client.get(reverse("chats:chat_list"))

        self.assertEqual(response.status_code, 200)

        # Check that pagination is active
        self.assertTrue(response.context["is_paginated"])

        # Check page description for paginated case (uses paginator.count)
        self.assertEqual(response.context["page_description"], "25 chats")
