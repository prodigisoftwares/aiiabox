from django.contrib.auth.models import User
from django.test import TestCase

from ..admin import UserProfileAdmin, UserSettingsAdmin
from ..models import UserProfile, UserSettings


class UserProfileAdminDisplayTestCase(TestCase):
    """Test UserProfileAdmin custom display methods."""

    def setUp(self):
        """Create test data."""
        self.admin = UserProfileAdmin(UserProfile, None)

        # Create user with full name
        self.user_with_name = User.objects.create_user(
            username="johndoe",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

        # Create user without full name
        self.user_no_name = User.objects.create_user(
            username="simple",
            password="testpass123",
        )

    def test_user_display_with_full_name(self):
        """Test user_display shows full name when available."""
        profile = self.user_with_name.profile
        result = self.admin.user_display(profile)

        self.assertEqual(result, "John Doe (johndoe)")

    def test_user_display_without_full_name(self):
        """Test user_display shows username when no full name."""
        profile = self.user_no_name.profile
        result = self.admin.user_display(profile)

        self.assertEqual(result, "simple")

    def test_has_avatar_without_avatar(self):
        """Test has_avatar returns False when no avatar."""
        profile = self.user_with_name.profile
        result = self.admin.has_avatar(profile)

        self.assertFalse(result)

    def test_has_avatar_with_avatar(self):
        """Test has_avatar returns True when avatar exists."""
        profile = self.user_with_name.profile
        # Set a dummy avatar (file doesn't need to exist for this test)
        profile.avatar = "avatars/2024/01/01/test.jpg"
        profile.save()

        result = self.admin.has_avatar(profile)

        self.assertTrue(result)


class UserSettingsAdminDisplayTestCase(TestCase):
    """Test UserSettingsAdmin custom display methods."""

    def setUp(self):
        """Create test data."""
        self.admin = UserSettingsAdmin(UserSettings, None)

        # Create user with full name
        self.user_with_name = User.objects.create_user(
            username="janesmith",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )

        # Create user without full name
        self.user_no_name = User.objects.create_user(
            username="simple",
            password="testpass123",
        )

    def test_user_display_with_full_name(self):
        """Test user_display shows full name when available."""
        settings = self.user_with_name.settings
        result = self.admin.user_display(settings)

        self.assertEqual(result, "Jane Smith (janesmith)")

    def test_user_display_without_full_name(self):
        """Test user_display shows username when no full name."""
        settings = self.user_no_name.settings
        result = self.admin.user_display(settings)

        self.assertEqual(result, "simple")
