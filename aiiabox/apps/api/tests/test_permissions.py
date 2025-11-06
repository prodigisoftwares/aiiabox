"""
Tests for API permission classes.

Covers:
- IsOwnerOrReadOnly permission
- User isolation
- Read vs write access control
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.api.permissions import IsOwnerOrReadOnly


class MockObject:
    """Mock object with user attribute for testing permissions."""

    def __init__(self, user=None, owner=None):
        self.user = user
        self.owner = owner


class IsOwnerOrReadOnlyTestCase(TestCase):
    """Test IsOwnerOrReadOnly permission class."""

    def setUp(self):
        """Create test users and request factory."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
        )
        self.factory = APIRequestFactory()
        self.permission = IsOwnerOrReadOnly()

    def test_read_access_allowed_to_authenticated_user(self):
        """Authenticated user can read any object."""
        request = self.factory.get("/")
        request.user = self.user1

        obj = MockObject(user=self.user2)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertTrue(result)

    def test_read_access_denied_to_unauthenticated_user(self):
        """Unauthenticated user cannot read objects."""
        request = self.factory.get("/")
        request.user = None

        obj = MockObject(user=self.user1)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertFalse(result)

    def test_write_access_allowed_to_owner(self):
        """Owner can write to their own object."""
        request = self.factory.post("/")
        request.user = self.user1

        obj = MockObject(user=self.user1)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertTrue(result)

    def test_write_access_denied_to_non_owner(self):
        """Non-owner cannot write to object."""
        request = self.factory.post("/")
        request.user = self.user1

        obj = MockObject(user=self.user2)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertFalse(result)

    def test_delete_access_allowed_to_owner(self):
        """Owner can delete their own object."""
        request = self.factory.delete("/")
        request.user = self.user1

        obj = MockObject(user=self.user1)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertTrue(result)

    def test_delete_access_denied_to_non_owner(self):
        """Non-owner cannot delete object."""
        request = self.factory.delete("/")
        request.user = self.user1

        obj = MockObject(user=self.user2)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertFalse(result)

    def test_works_with_owner_field_instead_of_user(self):
        """Permission works with 'owner' field instead of 'user' field."""
        request = self.factory.post("/")
        request.user = self.user1

        obj = MockObject(owner=self.user1)
        result = self.permission.has_object_permission(request, None, obj)

        self.assertTrue(result)

    def test_safe_methods_are_get_head_options(self):
        """GET, HEAD, OPTIONS are considered safe methods (read-only)."""
        obj = MockObject(user=self.user2)

        for method in ["get", "head", "options"]:
            request = getattr(self.factory, method)("/")
            request.user = self.user1
            result = self.permission.has_object_permission(request, None, obj)
            self.assertTrue(
                result, f"{method.upper()} should be allowed for authenticated users"
            )

    def test_write_methods_are_post_put_patch_delete(self):
        """POST, PUT, PATCH, DELETE require ownership."""
        obj = MockObject(user=self.user2)

        for method in ["post", "put", "patch", "delete"]:
            request = getattr(self.factory, method)("/")
            request.user = self.user1
            result = self.permission.has_object_permission(request, None, obj)
            self.assertFalse(result, f"{method.upper()} should require ownership")
