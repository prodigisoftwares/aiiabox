from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from .chat import Chat


class Message(models.Model):
    """
    Represents a single message in a conversation.

    Messages form the conversation history within a Chat. Each message
    has a role (user/assistant/system) to indicate its source, and stores
    token count for cost tracking and context window management.

    Assumes: Chat exists and user is authenticated
    Cascading delete: When Chat is deleted, all its Messages are deleted
    """

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):  # pragma: no cover
        return f"{self.role.capitalize()} - {self.created_at}"
