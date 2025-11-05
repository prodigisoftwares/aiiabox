from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Home page view that extends the base template.

    Demonstrates how child pages should extend base.html.
    Used for testing responsive navigation across viewports.
    """

    template_name = "core/home.html"
