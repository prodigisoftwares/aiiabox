from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from apps.api.serializers import TokenSerializer


class TokenView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving the current user's authentication token.

    Assumes:
    - User is authenticated via token authentication or session auth
    - User is already in the request object

    GET /api/auth/token/:
    - Returns: User's current token with creation timestamp
    - Status: 200 OK if user is authenticated
    - Status: 401 Unauthorized if user is not authenticated

    Note:
    - Token is created automatically by DRF when user is created
    - Same endpoint can be used to check if user already has token
    - Token is tied to User model and persists across requests
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TokenSerializer

    def get_object(self):  # pragma: no cover
        """Get or create token for authenticated user."""
        token, _created = Token.objects.get_or_create(user=self.request.user)
        return token
