from rest_framework import serializers
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for DRF Token model.

    Exposes token and created timestamp for API consumers.

    Fields:
    - token: The authentication token string (aliased from 'key' field)
    - created: ISO 8601 timestamp when token was created

    Usage:
    - GET /api/auth/token/ returns user's current token with creation time
    """

    token = serializers.CharField(source="key", read_only=True)

    class Meta:
        model = Token
        fields = ("token", "created")
