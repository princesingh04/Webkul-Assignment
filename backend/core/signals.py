# core/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Whenever a User is created, ensure a Profile exists.
    Also, when User is saved, we can update the profile if needed.
    """
    if created:
        # New user → create profile with a default username if missing
        username = instance.username or (instance.email.split("@")[0] if instance.email else f"user_{instance.pk}")
        # Ensure username is unique
        base_username = username
        counter = 1
        while Profile.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        Profile.objects.create(user=instance, username=username)
    else:
        # Existing user saved → just save related profile if it exists
        if hasattr(instance, "profile"):
            instance.profile.save()
