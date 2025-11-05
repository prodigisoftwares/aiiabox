from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    """
    Tests for login functionality.

    Verifies that:
    - Login page loads correctly
    - Valid credentials authenticate user
    - Invalid credentials show error messages
    - Authenticated users are redirected away from login
    """

    def setUp(self):
        """
        Set up test fixtures.

        Creates a test user and test client for authentication tests.
        """
        self.client = Client()
        self.login_url = reverse("core:login")
        self.home_url = reverse("core:home")

        # Create a test user
        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_page_loads(self):
        """
        Test that login page loads successfully.

        GET /login/ should return 200 status with login template.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/auth/login.html")

    def test_login_page_contains_form(self):
        """
        Test that login page contains form fields.

        Page should have username and password input fields.
        """
        response = self.client.get(self.login_url)
        self.assertContains(response, "username")
        self.assertContains(response, "password")
        self.assertContains(response, "Sign In")

    def test_valid_login_redirects_to_home(self):
        """
        Test that valid credentials redirect to home page.

        POST to /login/ with correct username/password should:
        - Authenticate user
        - Redirect to home page (302 status)
        - Set session cookie
        """
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "testpass123",
            },
            follow=True,
        )

        # Check redirect
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.home_url)

        # Check user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, "testuser")

    def test_invalid_username_shows_error(self):
        """
        Test that invalid username shows error message.

        POST with non-existent username should:
        - Return 200 status (not redirect)
        - Show error message
        - Not authenticate user
        """
        response = self.client.post(
            self.login_url,
            {
                "username": "wronguser",
                "password": "testpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        # Check for error message (case-insensitive)
        response_text = response.content.decode().lower()
        self.assertIn("failed", response_text)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_invalid_password_shows_error(self):
        """
        Test that invalid password shows error message.

        POST with correct username but wrong password should:
        - Return 200 status (not redirect)
        - Show error message
        - Not authenticate user
        """
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )

        self.assertEqual(response.status_code, 200)
        # Check for error message (case-insensitive)
        response_text = response.content.decode().lower()
        self.assertIn("failed", response_text)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_authenticated_user_redirected_from_login(self):
        """
        Test that authenticated users are redirected from login page.

        If user is already logged in and visits /login/:
        - Should redirect to home page
        """
        # Login first
        self.client.login(username="testuser", password="testpass123")

        # Try to access login page
        response = self.client.get(self.login_url)

        # Should redirect to home
        self.assertRedirects(response, self.home_url)

    def test_login_case_insensitive_username(self):
        """
        Test that username is case-insensitive for login.

        Django default: usernames are case-sensitive.
        This test documents the current behavior.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": "TestUser",  # Different case
                "password": "testpass123",
            },
        )

        # Django usernames ARE case-sensitive
        # So this should fail
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
