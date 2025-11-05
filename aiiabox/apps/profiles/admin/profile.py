from django.contrib import admin

from ..models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.

    Displays user profile information and allows editing of avatar, bio, and
    preferences. User field can be selected when creating new profiles.
    """

    list_display = ("user_display", "has_avatar", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
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
            "Profile Information",
            {"fields": ("avatar", "bio")},
        ),
        (
            "Preferences",
            {
                "fields": ("preferences",),
                "description": "JSON field for extensible user preferences",
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

    def has_avatar(self, obj):
        """Display whether user has an avatar."""
        return bool(obj.avatar)

    has_avatar.boolean = True
    has_avatar.short_description = "Has Avatar"
