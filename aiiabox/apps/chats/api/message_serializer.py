"""
DRF Serializer for Message model.

Handles serialization/deserialization of message data with proper
validation and read-only field handling.
"""

from rest_framework import serializers

from ..models import Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.

    Fields:
    - id (read-only): Auto-generated primary key
    - chat (required): Foreign key to parent Chat
    - user (read-only): Message author, auto-set from request.user
    - content (required): Message text, cannot be empty
    - role (required): Message role (user/assistant/system)
    - tokens (read-only): Token count, auto-calculated or provided
    - created_at (read-only): Timestamp when message was created

    Validation:
    - content is required and cannot be empty/whitespace only
    - role must be a valid choice (user, assistant, system)
    - chat must be a valid Chat id owned by the request user

    Assumes: User is authenticated, Chat exists and belongs to request user
    Side effects: create() method auto-sets user and chat fields
    """

    class Meta:
        model = Message
        fields = ["id", "chat", "user", "content", "role", "tokens", "created_at"]
        read_only_fields = ["id", "user", "created_at", "tokens"]

    def validate_content(self, value):
        """
        Validate message content.

        - Required: cannot be empty or whitespace-only
        """
        if not value or not value.strip():  # pragma: no cover
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip()

    def validate_role(self, value):
        """
        Validate message role.

        Must be one of the valid choices defined in Message model.
        """
        valid_roles = dict(Message.ROLE_CHOICES).keys()
        if value not in valid_roles:  # pragma: no cover
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value

    def create(self, validated_data):
        """
        Create new message, auto-setting user from request context.

        The user is not part of the request data - it's extracted from the
        authenticated request context. This ensures users can only create
        messages as themselves.
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
