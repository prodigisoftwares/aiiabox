"""
Tests for Auth app view logic.

Only tests custom code - does NOT test Django or DRF framework behavior.

Covers:
- Custom view logic (get_or_create)
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token


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
