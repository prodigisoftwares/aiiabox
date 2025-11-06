from django.contrib import admin

from apps.chats.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = [
        "chat_display",
        "user_display",
        "role",
        "content_preview",
        "created_at",
    ]
    list_filter = ["role", "created_at", "user"]
    search_fields = ["chat__title", "user__username", "content"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Message Information",
            {
                "fields": ("chat", "user", "role", "tokens"),
            },
        ),
        (
            "Content",
            {
                "fields": ("content",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
            },
        ),
    )

    def chat_display(self, obj):  # pragma: no cover
        """
        Display parent chat title for easy identification.

        Shows the chat title in the admin list view for quick reference
        to the parent conversation.
        """
        return obj.chat.title

    chat_display.short_description = "Chat"

    def user_display(self, obj):  # pragma: no cover
        """
        Display message author's full name or username.

        Shows full name if available, falls back to username for clarity
        in admin list view.
        """
        user = obj.user
        if user.get_full_name():
            return f"{user.get_full_name()} ({user.username})"
        return user.username

    user_display.short_description = "Author"

    def content_preview(self, obj):  # pragma: no cover
        """
        Display first 100 characters of message content.

        Provides quick preview of message content in admin list view,
        truncated for readability.
        """
        content = obj.content
        if len(content) > 100:
            return f"{content[:100]}..."
        return content

    content_preview.short_description = "Preview"
