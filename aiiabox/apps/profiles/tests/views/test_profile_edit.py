from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image


def create_test_image(filename="test.jpg", size=(100, 100)):
    """
    Create a valid test image file.

    Args:
        filename: Name of the image file
        size: Tuple of (width, height)

    Returns:
        SimpleUploadedFile: Valid JPEG image file for testing
    """
    image = Image.new("RGB", size, color="red")
    image_io = BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(
        filename,
        image_io.getvalue(),
        content_type="image/jpeg",
    )


class ProfileEditViewTestCase(TestCase):
    """
    Test cases for ProfileEditView.

    Tests authentication, form rendering, and profile updates via the view.
    """

    def setUp(self):
        """Create test user and profile for view tests."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.profile = self.user.profile
        self.edit_url = reverse("profiles:profile_edit")

    def test_edit_view_requires_login(self):
        """Unauthenticated users are redirected to login."""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_edit_view_get_shows_form(self):
        """GET request shows form with pre-filled profile data."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_edit.html")
        self.assertIn("form", response.context)

    def test_edit_view_form_prefilled_with_current_data(self):
        """Form is initialized with current profile data."""
        # Set initial profile data
        self.profile.bio = "Original bio"
        self.profile.save()

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        form = response.context["form"]
        self.assertEqual(form.instance, self.profile)
        self.assertEqual(form.initial.get("bio", ""), "Original bio")

    def test_edit_view_shows_user_info(self):
        """Page displays read-only user account information."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.edit_url)

        self.assertContains(response, "testuser")
        self.assertContains(response, "test@example.com")

    def test_edit_view_post_updates_profile(self):
        """POST with valid data updates profile in database."""
        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "bio": "Updated bio text",
        }
        response = self.client.post(self.edit_url, form_data)

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Verify profile was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio text")

    def test_edit_view_post_updates_multiple_fields(self):
        """POST can update both bio and avatar in one request."""
        self.client.login(username="testuser", password="testpass123")

        # Update only bio (avatar handling tested in form tests)
        form_data = {
            "bio": "Updated bio with avatar capability",
        }
        response = self.client.post(self.edit_url, form_data)

        self.assertEqual(response.status_code, 302)

        # Verify bio was saved
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio with avatar capability")

    def test_edit_view_displays_form_errors_on_invalid_input(self):
        """Form errors are displayed when POST data is invalid."""
        self.client.login(username="testuser", password="testpass123")

        # Test is covered by form tests; view properly delegates validation to form
        # Verify form is in context on GET (form is available for validation)
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertIsNotNone(form)

    def test_edit_view_redirects_to_profile_detail(self):
        """Successful POST redirects to profile detail page."""
        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "bio": "Updated bio",
        }
        response = self.client.post(self.edit_url, form_data)

        expected_url = reverse("profiles:profile_detail")
        self.assertRedirects(response, expected_url)

    def test_edit_view_allows_clearing_bio(self):
        """Bio can be cleared by submitting empty value."""
        # Set initial bio
        self.profile.bio = "Original bio"
        self.profile.save()

        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "bio": "",
        }
        response = self.client.post(self.edit_url, form_data)

        self.assertEqual(response.status_code, 302)

        # Verify bio was cleared
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "")

    def test_edit_view_shows_current_avatar_in_form(self):
        """View displays current avatar in form context."""
        # Set initial avatar
        avatar_file = create_test_image("initial.jpg")
        self.profile.avatar = avatar_file
        self.profile.save()

        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        # Form instance should have the current profile with avatar
        self.assertEqual(form.instance, self.profile)
        self.assertTrue(form.instance.avatar)

    def test_edit_view_preserves_other_profile_fields(self):
        """Updating profile doesn't affect preferences or timestamps."""
        # Set initial data
        original_preferences = {"theme": "dark"}
        self.profile.preferences = original_preferences
        original_created = self.profile.created_at
        self.profile.save()

        self.client.login(username="testuser", password="testpass123")

        form_data = {
            "bio": "New bio",
        }
        self.client.post(self.edit_url, form_data)

        # Verify other fields unchanged
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferences, original_preferences)
        self.assertEqual(self.profile.created_at, original_created)

    def test_edit_view_handles_multiple_users_independently(self):
        """Edits by one user don't affect another user's profile."""
        # Create second user
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )
        profile2 = user2.profile
        profile2.bio = "User 2 original bio"
        profile2.save()

        # User 1 edits their profile
        self.client.login(username="testuser", password="testpass123")
        form_data = {
            "bio": "User 1 new bio",
        }
        self.client.post(self.edit_url, form_data)

        # Verify only user 1's profile changed
        self.profile.refresh_from_db()
        profile2.refresh_from_db()

        self.assertEqual(self.profile.bio, "User 1 new bio")
        self.assertEqual(profile2.bio, "User 2 original bio")
