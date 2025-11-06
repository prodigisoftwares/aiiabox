"""
Signal handlers for API app.

Auto-creates authentication tokens for new users.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created, **kwargs):
    """
    Auto-create API token when new user is created.

    Assumes:
    - This signal is registered when User model is saved
    - Token model is available from rest_framework.authtoken

    Behavior:
    - Creates Token only on initial user creation (created=True)
    - Does not recreate token if user is updated
    - Token is tied to User via OneToOne relationship

    Usage:
    - Automatically called by Django when User is created
    - No manual intervention needed
    """
    if created:
        Token.objects.create(user=instance)
