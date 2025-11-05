from django.contrib.auth.models import User
from django.test import TestCase

from apps.profiles.forms import UserSettingsForm


class UserSettingsFormTestCase(TestCase):
    """
    Test cases for UserSettingsForm validation and behavior.

    Tests form initialization, field validation, and theme selection.
    """

    def setUp(self):
        """Create test user and settings for form tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.settings = self.user.settings

    def test_form_initializes_with_instance(self):
        """Form can be initialized with existing settings instance."""
        form = UserSettingsForm(instance=self.settings)
        self.assertIsNotNone(form.fields["theme"])

    def test_form_valid_with_light_theme(self):
        """Form is valid with light theme selection."""
        form_data = {
            "theme": "light",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_valid_with_dark_theme(self):
        """Form is valid with dark theme selection."""
        form_data = {
            "theme": "dark",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_valid_with_auto_theme(self):
        """Form is valid with auto (system) theme selection."""
        form_data = {
            "theme": "auto",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_form_rejects_invalid_theme(self):
        """Form rejects invalid theme values."""
        form_data = {
            "theme": "invalid_theme",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertFalse(form.is_valid())
        self.assertIn("theme", form.errors)

    def test_form_rejects_empty_theme(self):
        """Form rejects empty theme (required field)."""
        form_data = {
            "theme": "",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertFalse(form.is_valid())
        self.assertIn("theme", form.errors)

    def test_form_saves_theme_selection(self):
        """Form saves theme selection to database when valid."""
        form_data = {
            "theme": "dark",
        }
        form = UserSettingsForm(form_data, instance=self.settings)
        self.assertTrue(form.is_valid(), msg=form.errors)

        # Save the form
        updated_settings = form.save()

        # Verify theme was saved
        self.assertEqual(updated_settings.theme, "dark")

    def test_form_excludes_user_field(self):
        """Form does not include user field (should not be editable)."""
        form = UserSettingsForm()
        self.assertNotIn("user", form.fields)

    def test_form_excludes_default_project(self):
        """Form does not include default_project field."""
        form = UserSettingsForm()
        self.assertNotIn("default_project", form.fields)

    def test_form_excludes_llm_preferences(self):
        """Form does not include llm_preferences field."""
        form = UserSettingsForm()
        self.assertNotIn("llm_preferences", form.fields)

    def test_form_excludes_timestamps(self):
        """Form does not include created_at or updated_at fields."""
        form = UserSettingsForm()
        self.assertNotIn("created_at", form.fields)
        self.assertNotIn("updated_at", form.fields)

    def test_form_theme_field_has_radio_widget(self):
        """Theme field uses RadioSelect widget for better UX."""
        form = UserSettingsForm()
        from django.forms import RadioSelect

        self.assertIsInstance(form.fields["theme"].widget, RadioSelect)

    def test_form_includes_all_theme_choices(self):
        """Form theme field includes all available theme choices."""
        form = UserSettingsForm()
        theme_choices = [choice[0] for choice in form.fields["theme"].choices]
        self.assertIn("light", theme_choices)
        self.assertIn("dark", theme_choices)
        self.assertIn("auto", theme_choices)
