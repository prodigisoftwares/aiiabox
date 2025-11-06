from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API"

    def ready(self):
        """Register signal handlers when app is ready."""
        import apps.api.signals  # noqa: F401
