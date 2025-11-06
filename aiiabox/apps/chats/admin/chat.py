from django.contrib import admin

from apps.chats.models import Chat, Message


class MessageInline(admin.TabularInline):
    """Inline display of messages within chat admin."""

    model = Message
    fields = ["user", "role", "content", "tokens", "created_at"]
    readonly_fields = ["created_at"]
    extra = 0


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Admin interface for Chat model."""

    list_display = [
        "title",
        "user_display",
        "message_count",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at", "user"]
    search_fields = ["title", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [MessageInline]

    fieldsets = (
        (
            "Chat Information",
            {
                "fields": ("user", "title"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("metadata",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def user_display(self, obj):  # pragma: no cover
        """
        Display user's full name or username.

        Shows full name if available, falls back to username for clarity
        in admin list view.
        """
        user = obj.user
        if user.get_full_name():
            return f"{user.get_full_name()} ({user.username})"
        return user.username

    user_display.short_description = "User"

    def message_count(self, obj):  # pragma: no cover
        """Display the total number of messages in this chat."""
        return obj.messages.count()

    message_count.short_description = "Messages"
