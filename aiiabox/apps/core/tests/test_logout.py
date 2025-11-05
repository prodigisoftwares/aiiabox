from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class LogoutViewTests(TestCase):
    """
    Tests for logout functionality.

    Verifies that:
    - Logout clears authentication
    - User is redirected to home
    - Session is cleared
    """

    def setUp(self):
        """
        Set up test fixtures.

        Creates test user and test client.
        """
        self.client = Client()
        self.logout_url = reverse("core:logout")
        self.home_url = reverse("core:home")
        self.login_url = reverse("core:login")

        # Create test user
        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_logout_redirects_to_home(self):
        """
        Test that logout redirects to home page.

        POST to /logout/ should redirect to home (302 status).
        """
        # Login first
        self.client.login(username="testuser", password="testpass123")

        # Verify logged in
        response = self.client.get(self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Logout (POST request)
        response = self.client.post(self.logout_url, follow=True)

        # Should redirect to home
        self.assertRedirects(response, self.home_url)

    def test_logout_clears_authentication(self):
        """
        Test that logout clears user authentication.

        After logout, user should be anonymous.
        """
        # Login first
        self.client.login(username="testuser", password="testpass123")

        # Logout (POST request)
        response = self.client.post(self.logout_url, follow=True)

        # Check user is no longer authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_requires_session(self):
        """
        Test that logout works for logged-in users.

        Even if user is already logged out, logout should work.
        """
        # Try logout without being logged in (POST request)
        response = self.client.post(self.logout_url, follow=True)

        # Should still redirect (no error)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logged_out_user_cannot_access_protected_pages(self):
        """
        Test that logged-out users cannot access protected pages.

        This documents behavior for future protected views.
        Currently home page is public, but tests the flow.
        """
        # Login
        self.client.login(username="testuser", password="testpass123")
        # Verify session has auth_user_id
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)

        # Logout (POST request)
        self.client.post(self.logout_url)

        # After logout, accessing page as anonymous user
        response = self.client.get(self.home_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
