from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.chats.models import Chat
from apps.chats.views import (
    ChatCreateView,
    ChatDeleteView,
    ChatDetailView,
    ChatListView,
)


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
