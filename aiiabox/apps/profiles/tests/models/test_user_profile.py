from django.contrib.auth.models import User
from django.test import TestCase

from ...models import UserProfile


class UserProfileCreationTestCase(TestCase):
    """Test UserProfile model and auto-creation signals."""

    def test_user_profile_auto_created_on_user_creation(self):
        """Test that UserProfile is automatically created when User is created."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Profile should exist and be associated with the user
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)

    def test_user_profile_default_values(self):
        """Test UserProfile has correct default values on creation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        profile = user.profile

        self.assertEqual(profile.bio, "")
        self.assertFalse(profile.avatar)  # ImageField empty check
        self.assertEqual(profile.preferences, {})
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_user_profile_with_bio(self):
        """Test UserProfile can store bio."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        profile = user.profile
        profile.bio = "I love coding!"
        profile.save()

        # Refresh from database
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "I love coding!")

    def test_user_profile_with_preferences(self):
        """Test UserProfile can store JSON preferences."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        profile = user.profile
        profile.preferences = {"notifications": True, "language": "en"}
        profile.save()

        profile.refresh_from_db()
        self.assertEqual(profile.preferences["notifications"], True)
        self.assertEqual(profile.preferences["language"], "en")

    def test_user_profile_str_method_with_full_name(self):
        """Test UserProfile __str__ with user full name."""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        profile = user.profile

        expected = "John Doe - Profile"
        self.assertEqual(str(profile), expected)

    def test_user_profile_str_method_without_full_name(self):
        """Test UserProfile __str__ with only username."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        profile = user.profile

        expected = "testuser - Profile"
        self.assertEqual(str(profile), expected)

    def test_user_profile_deletion_cascades_from_user(self):
        """Test UserProfile is deleted when User is deleted."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        profile_id = user.profile.id

        user.delete()

        # Profile should be deleted
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())

    def test_user_profile_avatar_upload_path(self):
        """Test avatar field uses correct upload path."""
        User.objects.create_user(username="testuser", password="testpass123")

        # Check upload_to path contains date structure
        field = UserProfile._meta.get_field("avatar")
        self.assertEqual(field.upload_to, "avatars/%Y/%m/%d/")
