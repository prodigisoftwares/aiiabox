"""
Tests for Auth app token signals.

Only tests custom code - does NOT test Django or DRF framework behavior.

Covers:
- Token auto-creation signal
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
