from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

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


class CustomRegisterView(CreateView):
    """
    Custom register view with Tailwind styling.

    Uses UserCreationForm for user registration.
    Redirects to login page on successful registration.
    """

    template_name = "core/auth/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("core:login")


def handler_404(request, exception=None):
    """
    Handle 404 Page Not Found errors.

    Renders custom 404 error page with helpful navigation.
    """
    html = render_to_string("core/errors/404.html", request=request)
    return HttpResponse(html, status=404)


def handler_500(request):
    """
    Handle 500 Internal Server errors.

    Renders custom 500 error page with helpful navigation.
    """
    html = render_to_string("core/errors/500.html", request=request)
    return HttpResponse(html, status=500)
