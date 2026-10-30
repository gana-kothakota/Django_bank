from typing import Any, Type 
from django.conf import settings
from django.db.models import Model 
from django.dispatch import receiver
from django.db.models.signals import post_save
from loguru import logger

from core_apps.user_profile.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender: Type[Model], instance: Any, created: bool, **kwargs: Any) -> None:
    """Create a Profile for a new User when the user is created."""
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for new user: {instance.email}")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender: Type[Model], instance: Any, **kwargs: Any) -> None:
    """Save a Profile for a User when updated."""
    if hasattr(instance, "profile"):
        instance.profile.save()
