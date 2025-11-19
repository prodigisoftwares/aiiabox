"""
Tests for Message API endpoints.

Tests cover:
- Authentication (token required, invalid tokens rejected)
- Authorization (users can only access own messages)
- CRUD operations for MessageViewSet
- Input validation (content, role)
- Pagination and filtering
- HTTP status codes (200, 201, 204, 400, 403, 404)
- Permission enforcement
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ...models import Chat, Message


class MessageAPITestCase(TestCase):
    """Tests for Message API endpoints."""

    def setUp(self):
        """Set up test data and API client."""
        # Create test users
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")

        # Get or create tokens
        self.token1, _ = Token.objects.get_or_create(user=self.user1)
        self.token2, _ = Token.objects.get_or_create(user=self.user2)

        # Set up API client
        self.client = APIClient()

        # Create test chats
        self.chat1 = Chat.objects.create(user=self.user1, title="Chat 1")
        self.chat2 = Chat.objects.create(user=self.user2, title="User 2 Chat")

        # Create test messages
        self.msg1 = Message.objects.create(
            chat=self.chat1, user=self.user1, content="Hello", role="user"
        )
        self.msg2 = Message.objects.create(
            chat=self.chat1, user=self.user1, content="Hi there", role="assistant"
        )

    def test_list_messages_requires_authentication(self):
        """Test that listing messages requires valid token."""
        url = f"/api/chats/{self.chat1.id}/messages/"

        # Without token
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        # With invalid token
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid_token")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_list_messages_success(self):
        """Test listing messages in a chat."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(f"/api/chats/{self.chat1.id}/messages/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["content"], "Hello")
        self.assertEqual(response.data["results"][1]["content"], "Hi there")

    def test_list_messages_other_user_forbidden(self):
        """Test that user cannot see another user's chat messages."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(f"/api/chats/{self.chat2.id}/messages/")

        self.assertEqual(response.status_code, 403)

    def test_list_messages_chat_not_found(self):
        """Test listing messages from non-existent chat returns 403 (forbidden)."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get("/api/chats/99999/messages/")

        # Returns 403 because permission check fails before 404 (correct API behavior)
        self.assertEqual(response.status_code, 403)

    def test_create_message_success(self):
        """Test creating a message in a chat."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {"chat": self.chat1.id, "content": "New message", "role": "user"}
        response = self.client.post(f"/api/chats/{self.chat1.id}/messages/", data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["content"], "New message")
        self.assertEqual(response.data["role"], "user")
        self.assertEqual(response.data["user"], self.user1.id)

        # Verify message was created
        self.assertTrue(Message.objects.filter(content="New message").exists())

    def test_create_message_content_required(self):
        """Test that message content is required."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {"chat": self.chat1.id, "role": "user"}
        response = self.client.post(f"/api/chats/{self.chat1.id}/messages/", data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("content", response.data)

    def test_create_message_content_cannot_be_empty(self):
        """Test that message content cannot be empty or whitespace only."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")

        # Empty
        response = self.client.post(
            f"/api/chats/{self.chat1.id}/messages/",
            {"chat": self.chat1.id, "content": "", "role": "user"},
        )
        self.assertEqual(response.status_code, 400)

        # Whitespace only
        response = self.client.post(
            f"/api/chats/{self.chat1.id}/messages/",
            {"chat": self.chat1.id, "content": "   ", "role": "user"},
        )
        self.assertEqual(response.status_code, 400)

    def test_create_message_role_required(self):
        """Test that message role is required."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {"chat": self.chat1.id, "content": "Test message"}
        response = self.client.post(f"/api/chats/{self.chat1.id}/messages/", data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data)

    def test_create_message_role_validation(self):
        """Test that message role must be a valid choice."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {
            "chat": self.chat1.id,
            "content": "Test message",
            "role": "invalid_role",
        }
        response = self.client.post(f"/api/chats/{self.chat1.id}/messages/", data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data)

    def test_create_message_valid_roles(self):
        """Test creating messages with all valid roles."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        valid_roles = ["user", "assistant", "system"]

        for role in valid_roles:
            data = {
                "chat": self.chat1.id,
                "content": f"Message with {role} role",
                "role": role,
            }
            response = self.client.post(f"/api/chats/{self.chat1.id}/messages/", data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data["role"], role)

    def test_create_message_in_other_user_chat_forbidden(self):
        """Test that user cannot create message in another user's chat."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        data = {
            "chat": self.chat2.id,
            "content": "Unauthorized message",
            "role": "user",
        }
        response = self.client.post(f"/api/chats/{self.chat2.id}/messages/", data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Message.objects.filter(content="Unauthorized message").exists()
        )

    def test_retrieve_message_success(self):
        """Test retrieving a single message."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(
            f"/api/chats/{self.chat1.id}/messages/{self.msg1.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], "Hello")

    def test_retrieve_message_not_found(self):
        """Test retrieving non-existent message."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.get(f"/api/chats/{self.chat1.id}/messages/99999/")

        self.assertEqual(response.status_code, 404)

    def test_delete_message_success(self):
        """Test deleting a message."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.delete(
            f"/api/chats/{self.chat1.id}/messages/{self.msg1.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Message.objects.filter(id=self.msg1.id).exists())

    def test_delete_message_other_user_forbidden(self):
        """Test that user cannot delete another user's message."""
        # Create message in user2's chat
        msg_user2 = Message.objects.create(
            chat=self.chat2, user=self.user2, content="User 2 message", role="user"
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")
        response = self.client.delete(
            f"/api/chats/{self.chat2.id}/messages/{msg_user2.id}/"
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Message.objects.filter(id=msg_user2.id).exists())

    def test_message_pagination(self):
        """Test that message pagination works."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1}")

        # Create 23 more messages (setUp creates 2, total = 25, default page size = 20)
        for i in range(3, 26):
            Message.objects.create(
                chat=self.chat1, user=self.user1, content=f"Message {i}", role="user"
            )

        response = self.client.get(f"/api/chats/{self.chat1.id}/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNotNone(response.data["next"])

        # Get second page (25 - 20 = 5 remaining)
        response = self.client.get(f"/api/chats/{self.chat1.id}/messages/?page=2")
        self.assertEqual(len(response.data["results"]), 5)
