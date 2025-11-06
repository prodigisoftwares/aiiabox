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
        Display parent chat title as a clickable admin link.

        Shows the chat title and provides easy navigation to the parent chat
        in the admin interface.
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
