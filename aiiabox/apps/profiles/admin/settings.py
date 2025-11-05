from django.contrib import admin

from ..models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for UserSettings model.

    Displays user preferences and system settings. Allows manual creation
    of UserSettings for users that don't have one yet (normally auto-created
    via signal, but useful for testing or manual user setup).
    """

    list_display = ("user_display", "theme", "created_at", "updated_at")
    list_filter = ("theme", "created_at", "updated_at")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "UI Settings",
            {"fields": ("theme",)},
        ),
        (
            "Default Project",
            {
                "fields": ("default_project",),
                "description": "Default project for new chats (Phase 4)",
                "classes": ("collapse",),
            },
        ),
        (
            "LLM Preferences",
            {
                "fields": ("llm_preferences",),
                "description": "JSON field: model, temperature, max_tokens, etc.",
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_display(self, obj):
        """Display user with full name and username."""
        full_name = obj.user.get_full_name()
        username = obj.user.username
        return f"{full_name} ({username})" if full_name else username

    user_display.short_description = "User"
