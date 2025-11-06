from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "apps_auth"

    def ready(self):
        """Import signals when app is ready."""
        import apps.auth.signals  # noqa
