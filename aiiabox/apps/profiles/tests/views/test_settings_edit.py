from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SettingsEditViewTestCase(TestCase):
    """
    Test cases for SettingsEditView.

    Tests authentication, form rendering, and settings updates via the view.
    """

    def setUp(self):
        """Create test user and settings for view tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = self.user.settings
        self.edit_url = reverse("profiles:settings_edit")

    def test_edit_view_requires_login(self):
        """Unauthenticated users are redirected to login."""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_edit_view_get_shows_form(self):
        """GET request shows form with pre-filled settings data."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/settings_edit.html")
        self.assertIn("form", response.context)

    def test_edit_view_form_prefilled_with_current_theme(self):
        """Form is initialized with current theme setting."""
        # Set initial theme
        self.settings.theme = "dark"
        self.settings.save()

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        form = response.context["form"]
        self.assertEqual(form.instance, self.settings)
        self.assertEqual(form.initial.get("theme"), "dark")

    def test_edit_view_post_updates_settings(self):
        """POST with valid data updates settings in database."""
        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "theme": "dark",
        }
        response = self.client.post(self.edit_url, form_data)

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Verify settings were updated
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.theme, "dark")

    def test_edit_view_updates_to_light_theme(self):
        """Can update settings from auto theme to light theme."""
        # Set initial theme to auto
        self.settings.theme = "auto"
        self.settings.save()

        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "theme": "light",
        }
        response = self.client.post(self.edit_url, form_data)

        self.assertEqual(response.status_code, 302)

        # Verify theme was updated
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.theme, "light")

    def test_edit_view_updates_to_auto_theme(self):
        """Can update settings back to auto (system preference) theme."""
        # Set initial theme to dark
        self.settings.theme = "dark"
        self.settings.save()

        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "theme": "auto",
        }
        response = self.client.post(self.edit_url, form_data)

        self.assertEqual(response.status_code, 302)

        # Verify theme was updated
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.theme, "auto")

    def test_edit_view_displays_form_errors_on_invalid_input(self):
        """Form errors are displayed when POST data is invalid."""
        self.client.login(username="testuser", password="testpass123")

        # Post with invalid theme value
        form_data = {
            "theme": "invalid_theme",
        }
        response = self.client.post(self.edit_url, form_data)

        # Should re-render form with errors (400 or 200 depending on Django version)
        self.assertIn(response.status_code, [200, 400])
        # Form should be in context
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())

    def test_edit_view_redirects_to_profile_detail(self):
        """Successful POST redirects to profile detail page."""
        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "theme": "dark",
        }
        response = self.client.post(self.edit_url, form_data)

        expected_url = reverse("profiles:profile_detail")
        self.assertRedirects(response, expected_url)

    def test_edit_view_preserves_other_settings_fields(self):
        """Updating theme doesn't affect other settings fields."""
        # Set initial data
        original_llm_prefs = {"model": "test"}
        self.settings.llm_preferences = original_llm_prefs
        original_created = self.settings.created_at
        self.settings.save()

        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "theme": "dark",
        }
        self.client.post(self.edit_url, form_data)

        # Verify other fields unchanged
        self.settings.refresh_from_db()
        self.assertEqual(self.settings.llm_preferences, original_llm_prefs)
        self.assertEqual(self.settings.created_at, original_created)

    def test_edit_view_handles_multiple_users_independently(self):
        """Changes by one user don't affect another user's settings."""
        # Create second user
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        settings2 = user2.settings
        settings2.theme = "light"
        settings2.save()

        # User 1 edits their settings
        self.client.login(username="testuser", password="testpass123")
        form_data = {
            "theme": "dark",
        }
        self.client.post(self.edit_url, form_data)

        # Verify only user 1's settings changed
        self.settings.refresh_from_db()
        settings2.refresh_from_db()

        self.assertEqual(self.settings.theme, "dark")
        self.assertEqual(settings2.theme, "light")

    def test_edit_view_default_theme_is_auto(self):
        """New settings have auto theme as default."""
        # Create new user (settings auto-created via signal)
        User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="testpass123",
        )

        self.client.login(username="newuser", password="testpass123")
        response = self.client.get(self.edit_url)

        form = response.context["form"]
        self.assertEqual(form.instance.theme, "auto")

    def test_edit_view_displays_settings_page_title(self):
        """Settings page displays appropriate title and description."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        # Check for page heading (will be in template)
        self.assertContains(response, "Settings")
