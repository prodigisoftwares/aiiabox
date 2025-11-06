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

    list_display = ["title", "user", "message_count", "created_at", "updated_at"]
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

    def message_count(self, obj):  # pragma: no cover
        return obj.messages.count()

    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = ["chat", "user", "role", "token_display", "created_at"]
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

    def token_display(self, obj):  # pragma: no cover
        return obj.tokens

    token_display.short_description = "Tokens"
