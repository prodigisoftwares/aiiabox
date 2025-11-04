from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, UserSettings


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to auto-create UserProfile when a new User is created.

    This ensures every User has an associated UserProfile without requiring
    explicit creation in signup views.

    Args:
        sender: The User model class
        instance: The User instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """
    Signal handler to auto-create UserSettings when a new User is created.

    This ensures every User has default settings configured without requiring
    explicit creation in signup views.

    Args:
        sender: The User model class
        instance: The User instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    if created:
        UserSettings.objects.create(user=instance)
