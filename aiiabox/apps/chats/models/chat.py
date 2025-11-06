from django.contrib.auth.models import User
from django.db import models


class Chat(models.Model):
    """
    Represents a conversation thread owned by a user.

    A Chat contains multiple Messages that form a conversation history.
    Metadata is stored as JSON for flexibility to add future features
    (system_prompt, model_name, settings) without schema migrations.

    Assumes: User is authenticated and owns this chat
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
        ]

    def __str__(self):  # pragma: no cover
        return self.title
