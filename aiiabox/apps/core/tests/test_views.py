from django.contrib.auth.models import User
from django.test import TestCase


class HomeViewTests(TestCase):
    """Test home view and base template rendering."""

    def test_home_view_renders_base_template(self):
        """Verify home view returns successful response with base template content."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Platform")

    def test_home_view_shows_login_for_anonymous_users(self):
        """Anonymous users should see sign in link in sidebar."""
        response = self.client.get("/")
        self.assertContains(response, "Sign In")

    def test_home_view_shows_dashboard_for_authenticated_users(self):
        """Authenticated users should see dashboard and settings links."""
        User.objects.create_user("testuser", "test@example.com", "testpass")
        self.client.login(username="testuser", password="testpass")

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "Settings")

    def test_home_view_shows_logout_for_authenticated_users(self):
        """Authenticated users should see logout link."""
        User.objects.create_user("testuser", "test@example.com", "testpass")
        self.client.login(username="testuser", password="testpass")

        response = self.client.get("/")
        self.assertContains(response, "Logout")

    def test_navigation_component_renders(self):
        """Verify navigation component is included in all pages."""
        response = self.client.get("/")
        self.assertContains(response, "AI Platform")
        self.assertContains(response, "nav")

    def test_sidebar_renders(self):
        """Verify sidebar navigation is rendered."""
        response = self.client.get("/")
        self.assertContains(response, "AI Platform")


class ErrorPageTests(TestCase):
    """Test error page templates."""

    def test_404_page_returns_not_found_status(self):
        """Verify 404 responses are returned for nonexistent pages."""
        response = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)
