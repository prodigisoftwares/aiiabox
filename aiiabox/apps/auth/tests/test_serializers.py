"""
Tests for Auth app serializers.

Only tests custom code - does NOT test Django or DRF framework behavior.

Covers:
- Token serialization
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token


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

        from apps.auth.serializers import TokenSerializer

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

        from apps.auth.serializers import TokenSerializer

        serializer = TokenSerializer(token)

        # User field should not be in response
        self.assertNotIn("user", serializer.data)
