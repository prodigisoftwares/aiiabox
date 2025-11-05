from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

from .forms import CustomAuthenticationForm


class HomeView(TemplateView):
    """
    Home page view that extends the base template.

    Demonstrates how child pages should extend base.html.
    Used for testing responsive navigation across viewports.
    """

    template_name = "core/home.html"


class CustomLoginView(LoginView):
    """
    Custom login view with Tailwind styling.

    Uses CustomAuthenticationForm for consistent styling across all form inputs.
    Redirects authenticated users to home page on successful login.
    """

    template_name = "core/auth/login.html"
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """
    Custom logout view.

    Logs out the user and redirects to home page.
    """

    next_page = "core:home"
