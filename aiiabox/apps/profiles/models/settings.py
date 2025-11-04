from django.contrib.auth.models import User
from django.db import models


class UserSettings(models.Model):
    """
    User settings model for storing system preferences and configuration.

    Separate from UserProfile to keep account/system settings distinct from
    personal user information.

    Fields:
        user: OneToOne relationship to User model (CASCADE delete)
        theme: UI theme preference (light/dark/auto)
        default_project: Default project for new chats (optional, FK to Project)
        llm_preferences: JSON field for LLM-specific settings
            Default structure:
            {
                "model": "llama2",
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.95,
                "top_k": 40
            }
        created_at: Timestamp of settings creation
        updated_at: Timestamp of last update

    Auto-created: A UserSettings is automatically created when a new User
    is created via post_save signal in signals.py

    Note: default_project is nullable to handle the case where no projects
    exist yet. This reference will be populated in Phase 4 (Projects).
    """

    THEME_CHOICES = (
        ("light", "Light"),
        ("dark", "Dark"),
        ("auto", "Auto (System Preference)"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="auto",
        help_text="UI theme preference",
    )
    default_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_for_users",
        help_text="Default project for new chats (added in Phase 4)",
    )
    llm_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="LLM configuration: model, temperature, max_tokens, etc.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):  # pragma: no cover
        return f"{self.user.get_full_name() or self.user.username} - Settings"

    def get_llm_setting(self, key, default=None):
        """
        Safely retrieve an LLM preference setting.

        Args:
            key: Setting key (e.g., "model", "temperature")
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.llm_preferences.get(key, default)
