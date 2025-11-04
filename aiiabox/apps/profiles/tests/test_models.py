from django.contrib.auth.models import User
from django.test import TestCase

from ..models import UserProfile, UserSettings


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


class UserSettingsCreationTestCase(TestCase):
    """Test UserSettings model and auto-creation signals."""

    def test_user_settings_auto_created_on_user_creation(self):
        """Test that UserSettings is automatically created when User is created."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Settings should exist and be associated with the user
        self.assertTrue(hasattr(user, "settings"))
        self.assertIsInstance(user.settings, UserSettings)
        self.assertEqual(user.settings.user, user)

    def test_user_settings_default_values(self):
        """Test UserSettings has correct default values on creation."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings

        self.assertEqual(settings.theme, "auto")
        self.assertIsNone(settings.default_project)
        self.assertEqual(settings.llm_preferences, {})
        self.assertIsNotNone(settings.created_at)
        self.assertIsNotNone(settings.updated_at)

    def test_user_settings_theme_choices(self):
        """Test UserSettings accepts valid theme choices."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings

        # Test light theme
        settings.theme = "light"
        settings.save()
        settings.refresh_from_db()
        self.assertEqual(settings.theme, "light")

        # Test dark theme
        settings.theme = "dark"
        settings.save()
        settings.refresh_from_db()
        self.assertEqual(settings.theme, "dark")

        # Test auto theme (default)
        settings.theme = "auto"
        settings.save()
        settings.refresh_from_db()
        self.assertEqual(settings.theme, "auto")

    def test_user_settings_llm_preferences(self):
        """Test UserSettings can store LLM preferences."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings
        settings.llm_preferences = {
            "model": "llama2",
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40,
        }
        settings.save()

        settings.refresh_from_db()
        self.assertEqual(settings.llm_preferences["model"], "llama2")
        self.assertEqual(settings.llm_preferences["temperature"], 0.7)
        self.assertEqual(settings.llm_preferences["max_tokens"], 2048)

    def test_user_settings_get_llm_setting_existing_key(self):
        """Test get_llm_setting retrieves existing setting."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings
        settings.llm_preferences = {"model": "llama2", "temperature": 0.7}
        settings.save()

        self.assertEqual(settings.get_llm_setting("model"), "llama2")
        self.assertEqual(settings.get_llm_setting("temperature"), 0.7)

    def test_user_settings_get_llm_setting_missing_key_with_default(self):
        """Test get_llm_setting returns default for missing key."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings
        settings.llm_preferences = {"model": "llama2"}
        settings.save()

        result = settings.get_llm_setting("temperature", default=0.5)
        self.assertEqual(result, 0.5)

    def test_user_settings_get_llm_setting_missing_key_without_default(self):
        """Test get_llm_setting returns None for missing key without default."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings

        result = settings.get_llm_setting("nonexistent")
        self.assertIsNone(result)

    def test_user_settings_str_method_with_full_name(self):
        """Test UserSettings __str__ with user full name."""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Jane",
            last_name="Smith",
        )
        settings = user.settings

        expected = "Jane Smith - Settings"
        self.assertEqual(str(settings), expected)

    def test_user_settings_str_method_without_full_name(self):
        """Test UserSettings __str__ with only username."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings = user.settings

        expected = "testuser - Settings"
        self.assertEqual(str(settings), expected)

    def test_user_settings_deletion_cascades_from_user(self):
        """Test UserSettings is deleted when User is deleted."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        settings_id = user.settings.id

        user.delete()

        # Settings should be deleted
        self.assertFalse(UserSettings.objects.filter(id=settings_id).exists())

    def test_multiple_users_have_independent_settings(self):
        """Test multiple users have independent settings."""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")

        user1.settings.theme = "light"
        user1.settings.save()

        user2.settings.theme = "dark"
        user2.settings.save()

        user1.settings.refresh_from_db()
        user2.settings.refresh_from_db()

        self.assertEqual(user1.settings.theme, "light")
        self.assertEqual(user2.settings.theme, "dark")
