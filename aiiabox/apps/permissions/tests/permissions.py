"""
Tests for Permissions app permission classes.

Only tests custom permission logic - does NOT test Django REST framework behavior.
"""

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from rest_framework.permissions import SAFE_METHODS

from apps.permissions.permissions import IsOwnerOrReadOnly


class MockObject:
    """Mock object for testing permissions."""

    def __init__(self, user):
        self.user = user


class IsOwnerOrReadOnlyTestCase(TestCase):
    """Test IsOwnerOrReadOnly permission class."""

    def setUp(self):
        """Set up test users and request factory."""
        self.factory = RequestFactory()
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass123",
        )
        self.unauthenticated_user = None

    def test_read_permission_allowed_for_authenticated_user(self):
        """Authenticated users can read any object."""
        permission = IsOwnerOrReadOnly()
        obj = MockObject(self.owner)

        # Test all safe methods
        for method in SAFE_METHODS:
            request = self.factory.generic(method, "/")
            request.user = self.other_user  # Different user than object owner

            self.assertTrue(
                permission.has_object_permission(request, None, obj),
                f"Read permission should be allowed for {method} method",
            )

    def test_read_permission_denied_for_unauthenticated_user(self):
        """Unauthenticated users cannot read objects."""
        permission = IsOwnerOrReadOnly()
        obj = MockObject(self.owner)

        request = self.factory.get("/")
        request.user = self.unauthenticated_user

        self.assertFalse(permission.has_object_permission(request, None, obj))

    def test_write_permission_allowed_for_owner(self):
        """Object owners can modify their objects."""
        permission = IsOwnerOrReadOnly()
        obj = MockObject(self.owner)

        # Test unsafe methods
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            request = self.factory.generic(method, "/")
            request.user = self.owner  # Same user as object owner

            self.assertTrue(
                permission.has_object_permission(request, None, obj),
                f"Write permission should be allowed for owner with {method} method",
            )

    def test_write_permission_denied_for_non_owner(self):
        """Non-owners cannot modify objects."""
        permission = IsOwnerOrReadOnly()
        obj = MockObject(self.owner)

        # Test unsafe methods
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]
        for method in unsafe_methods:
            request = self.factory.generic(method, "/")
            request.user = self.other_user  # Different user than object owner

            self.assertFalse(
                permission.has_object_permission(request, None, obj),
                f"Write permission should be denied for non-owner with {method} method",
            )

    def test_write_permission_denied_for_unauthenticated_user(self):
        """Unauthenticated users cannot modify objects."""
        permission = IsOwnerOrReadOnly()
        obj = MockObject(self.owner)

        request = self.factory.post("/")
        request.user = self.unauthenticated_user

        self.assertFalse(permission.has_object_permission(request, None, obj))

    def test_permission_works_with_owner_attribute(self):
        """Permission class also works with 'owner' attribute."""
        permission = IsOwnerOrReadOnly()

        class MockObjectWithOwner:
            def __init__(self, owner):
                self.owner = owner

        obj = MockObjectWithOwner(self.owner)

        # Owner should have write permission
        request = self.factory.put("/")
        request.user = self.owner
        self.assertTrue(permission.has_object_permission(request, None, obj))

        # Non-owner should not have write permission
        request = self.factory.put("/")
        request.user = self.other_user
        self.assertFalse(permission.has_object_permission(request, None, obj))
