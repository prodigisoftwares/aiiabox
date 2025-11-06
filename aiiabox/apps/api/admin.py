from django.contrib import admin
from rest_framework.authtoken.models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """
    Admin interface for managing API tokens.

    Displays:
    - user: Link to user account
    - token: The authentication token (read-only for security)
    - created: Timestamp when token was created

    Actions:
    - View token details
    - Delete token to revoke access
    - Regenerate token by deleting and letting system recreate

    Notes:
    - Token field is read-only to prevent accidental modification
    - Deleting a token revokes API access for that user
    - Token is automatically recreated when user makes next API request
    - Users should store tokens securely (env vars, secrets manager)
    """

    list_display = ("user_display", "token_preview", "created")
    list_filter = ("created",)
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    readonly_fields = ("token_display", "created", "user")
    ordering = ("-created",)
    fields = ("user", "token_display", "created")

    def user_display(self, obj):
        """Display user with full name if available, else username."""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return obj.user.username

    user_display.short_description = "User"

    def token_preview(self, obj):
        """Display token preview (first 10 chars + ... + last 10 chars) for security in list view."""
        if len(obj.token) > 20:
            return f"{obj.token[:10]}...{obj.token[-10:]}"
        return obj.token

    token_preview.short_description = "Token"

    def token_display(self, obj):
        """Display full token in detail form (read-only)."""
        return obj.token

    token_display.short_description = "Token (Read-Only)"

    def has_add_permission(self, request):
        """Prevent manual token creation - tokens auto-created via signals."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow token deletion to revoke access."""
        return request.user.is_staff
