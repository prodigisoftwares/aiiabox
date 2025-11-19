"""
DRF Serializer for Chat model.

Handles serialization/deserialization of chat data with proper
validation and read-only field handling.
"""

from rest_framework import serializers

from ..models import Chat


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for Chat model.

    Fields:
    - id (read-only): Auto-generated primary key
    - user (read-only): Chat owner, auto-set from request.user
    - title (optional): Chat title, defaults to "Chat" if not provided, max 200 chars
    - created_at (read-only): Timestamp when chat was created
    - updated_at (read-only): Timestamp when chat was last updated
    - message_count (read-only): Computed count of messages in chat

    Validation:
    - title is optional; if provided, cannot be empty/whitespace only
    - title max length is 200 characters

    Assumes: User is authenticated (enforced by view permission classes)
    """

    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "user", "title", "created_at", "updated_at", "message_count"]
        read_only_fields = ["id", "user", "created_at", "updated_at", "message_count"]

    def get_message_count(self, obj):
        """
        Return count of messages in this chat.

        Used for displaying conversation size without loading all messages.
        """
        return obj.messages.count()

    def validate_title(self, value):
        """
        Validate chat title.

        - Required: cannot be empty or whitespace-only
        - Max length: enforced by model field, but check here for clarity
        """
        if not value or not value.strip():  # pragma: no cover
            raise serializers.ValidationError(
                "Title cannot be empty or whitespace only."
            )
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value.strip()
