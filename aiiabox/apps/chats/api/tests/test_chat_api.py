"""
Tests for Chat API endpoints.

Tests cover:
- Authentication (token required, invalid tokens rejected)
- Authorization (users can only access own chats)
- CRUD operations for ChatViewSet
- Input validation (title)
- Pagination and filtering
- HTTP status codes (200, 201, 204, 400, 403, 404)
- Permission enforcement
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ...models import Chat


class ChatAPITestCase(TestCase):
    """Tests for Chat API endpoints."""

    def setUp(self):
        """Set up test data and API client."""
        # Create test users
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")

        # Get or create tokens for authentication
        self.token1, _ = Token.objects.get_or_create(user=self.user1)
        self.token2, _ = Token.objects.get_or_create(user=self.user2)

        # Set up API client
        self.client = APIClient()

        # Create test chats
        self.chat1 = Chat.objects.create(user=self.user1, title="Chat 1")
        self.chat2 = Chat.objects.create(user=self.user1, title="Chat 2")
        self.chat3 = Chat.objects.create(user=self.user2, title="User 2 Chat")

    def test_list_chats_requires_authentication(self):
        """Test that listing chats requires valid token."""
        # Without token
        response = self.client.get("/api/chats/")
        self.assertEqual(response.status_code, 401)

        # With invalid token
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token_here")
        response = self.client.get("/api/chats/")
        self.assertEqual(response.status_code, 401)

    def test_list_chats_returns_user_chats_only(self):
        """Test that user only sees their own chats."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get("/api/chats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # User 1 has 2 chats
        chat_titles = [chat["title"] for chat in response.data["results"]]
        self.assertIn("Chat 1", chat_titles)
        self.assertIn("Chat 2", chat_titles)
        self.assertNotIn("User 2 Chat", chat_titles)

    def test_list_chats_pagination(self):
        """Test that pagination works on chat list."""
        # Create 23 more chats (setUp creates 2, total = 25, default page size = 20)
        for i in range(3, 26):
            Chat.objects.create(user=self.user1, title=f"Chat {i}")

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get("/api/chats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 20)  # First page
        self.assertIsNotNone(response.data["next"])

        # Get second page (25 - 20 = 5 remaining)
        response = self.client.get("/api/chats/?page=2")
        self.assertEqual(len(response.data["results"]), 5)  # Remaining chats

    def test_create_chat_success(self):
        """Test creating a new chat with valid title."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {"title": "New Chat"}
        response = self.client.post("/api/chats/", data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "New Chat")
        self.assertEqual(response.data["user"], self.user1.id)
        self.assertEqual(response.data["message_count"], 0)

        # Verify chat was created in database
        self.assertTrue(Chat.objects.filter(title="New Chat", user=self.user1).exists())

    def test_create_chat_title_required(self):
        """Test that chat title is required."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.post("/api/chats/", {})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)

    def test_create_chat_title_cannot_be_empty(self):
        """Test that title cannot be empty or whitespace only."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")

        # Empty string
        response = self.client.post("/api/chats/", {"title": ""})
        self.assertEqual(response.status_code, 400)

        # Whitespace only
        response = self.client.post("/api/chats/", {"title": "   "})
        self.assertEqual(response.status_code, 400)

    def test_create_chat_title_max_length(self):
        """Test that title cannot exceed 200 characters."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        long_title = "A" * 201
        response = self.client.post("/api/chats/", {"title": long_title})

        self.assertEqual(response.status_code, 400)

    def test_retrieve_chat_success(self):
        """Test retrieving a single chat."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(f"/api/chats/{self.chat1.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Chat 1")
        self.assertEqual(response.data["user"], self.user1.id)

    def test_retrieve_chat_not_found(self):
        """Test retrieving non-existent chat returns 404."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get("/api/chats/99999/")

        self.assertEqual(response.status_code, 404)

    def test_retrieve_other_user_chat_forbidden(self):
        """Test that user cannot access another user's chat (returns 404, not 403)."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(f"/api/chats/{self.chat3.id}/")

        # Returns 404 because chat is filtered out of user's queryset
        # (more secure - doesn't leak existence of other users' chats)
        self.assertEqual(response.status_code, 404)

    def test_delete_chat_success(self):
        """Test deleting a chat."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.delete(f"/api/chats/{self.chat1.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Chat.objects.filter(id=self.chat1.id).exists())

    def test_delete_chat_other_user_forbidden(self):
        """Test that user cannot delete another user's chat (returns 404)."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.delete(f"/api/chats/{self.chat3.id}/")

        # Returns 404 because chat is filtered out of user's queryset
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Chat.objects.filter(id=self.chat3.id).exists())
