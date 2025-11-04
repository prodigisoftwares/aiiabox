from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    User profile model for storing user-visible personal information.

    Separate from Django's User model which handles authentication.
    OneToOne relationship allows extending User data without modifying the
    built-in User model.

    Fields:
        user: OneToOne relationship to User model (CASCADE delete)
        avatar: Optional profile picture (stored in uploads/%Y/%m/%d/)
        bio: Optional user biography or description
        preferences: JSON field for extensible user preferences
            Default structure: {}
            Can store: theme preference, notification settings, etc.
        created_at: Timestamp of profile creation
        updated_at: Timestamp of last update

    Auto-created: A UserProfile is automatically created when a new User
    is created via post_save signal in signals.py
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="User profile picture",
    )
    bio = models.TextField(
        blank=True,
        default="",
        help_text="User biography or description",
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extensible user preferences (theme, notifications, etc.)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover
        return f"{self.user.get_full_name() or self.user.username} - Profile"
