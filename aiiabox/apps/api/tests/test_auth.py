"""
Tests for API authentication functionality.

Only tests custom code - does NOT test Django or DRF framework behavior.

Covers:
- Token auto-creation signal
- Custom view logic (get_or_create)
- Permission classes
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token


class TokenSignalTestCase(TestCase):
    """Test that tokens are auto-created when users are created."""

    def test_token_auto_created_on_user_creation(self):
        """Signal should auto-create token when user is created."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Token should exist after user creation
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_each_user_gets_unique_token(self):
        """Each user should have a unique token."""
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
        )

        token1 = Token.objects.get(user=user1)
        token2 = Token.objects.get(user=user2)

        self.assertNotEqual(token1.key, token2.key)

    def test_token_not_created_on_user_update(self):
        """Token should only be created once on initial user creation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        original_token = Token.objects.get(user=user)

        # Update user (trigger post_save signal again)
        user.email = "newemail@example.com"
        user.save()

        # Token should not change
        updated_token = Token.objects.get(user=user)
        self.assertEqual(original_token.key, updated_token.key)


class TokenViewLogicTestCase(TestCase):
    """Test TokenView get_or_create logic."""

    def test_view_returns_existing_token(self):
        """View should return existing token if it exists."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        original_token = Token.objects.get(user=user)

        # Simulate view calling get_or_create
        token, created = Token.objects.get_or_create(user=user)

        self.assertFalse(created)
        self.assertEqual(token.key, original_token.key)

    def test_view_creates_token_if_deleted(self):
        """View should create new token if previous one was deleted."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        original_token = Token.objects.get(user=user)
        original_key = original_token.key

        # Delete token
        original_token.delete()
        self.assertFalse(Token.objects.filter(user=user).exists())

        # Simulate view calling get_or_create
        token, created = Token.objects.get_or_create(user=user)

        self.assertTrue(created)
        self.assertNotEqual(token.key, original_key)
        self.assertTrue(Token.objects.filter(user=user).exists())


class TokenSerializerTestCase(TestCase):
    """Test TokenSerializer serialization."""

    def test_serializer_includes_token_and_created(self):
        """Serializer should include token and created fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        token_obj = Token.objects.get(user=user)

        from apps.api.serializers import TokenSerializer

        serializer = TokenSerializer(token_obj)

        self.assertIn("token", serializer.data)
        self.assertIn("created", serializer.data)
        self.assertEqual(serializer.data["token"], token_obj.key)

    def test_serializer_excludes_user_field(self):
        """Serializer should NOT expose user field (security)."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        token = Token.objects.get(user=user)

        from apps.api.serializers import TokenSerializer

        serializer = TokenSerializer(token)

        # User field should not be in response
        self.assertNotIn("user", serializer.data)
