from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow users to only access/modify their own resources.

    Assumes:
    - Object has an 'user' attribute or 'owner' attribute
    - User is authenticated via token authentication

    Returns:
    - Write operations allowed only if user owns the object
    - Read operations allowed if user is authenticated
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user or obj.owner == request.user
