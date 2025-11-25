import uuid
import os
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.db.models import F
from django.utils import timezone

User = get_user_model()


def upload_to_profile(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"profiles/{uuid.uuid4().hex}{ext}"


def upload_to_post(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"posts/{uuid.uuid4().hex}{ext}"


class Profile(models.Model):
    """
    OneToOne profile for the Django user.
    Keeps username, bio, profile image, etc.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to=upload_to_profile, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.user.email if self.user and hasattr(self.user, 'email') else self.pk})"


class Post(models.Model):
    """
    A user uploaded post (image + description). Stores cached like/dislike counts
    but authoritative data is in PostReaction rows.
    """
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to=upload_to_post)
    description = models.TextField(blank=True, max_length=1000)
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Post {self.pk} by {self.author.username}"

    def refresh_counts_from_reactions(self):
        """Utility to rebuild counts from PostReaction table (useful for audits)."""
        from django.db.models import Sum, Q
        agg = self.reactions.aggregate(
            likes=Sum('reaction', filter=Q(reaction=1)),
            dislikes=Sum('reaction', filter=Q(reaction=-1))
        )
        # agg may return None; compute safely
        likes = self.reactions.filter(reaction=1).count()
        dislikes = self.reactions.filter(reaction=-1).count()
        self.likes_count = likes
        self.dislikes_count = dislikes
        self.save(update_fields=['likes_count', 'dislikes_count'])


class PostReaction(models.Model):
    """
    Tracks a single user's reaction to a single post.
    reaction: 1 => like, -1 => dislike
    unique_together on (user, post) ensures one reaction per user per post.
    """
    REACTION_CHOICES = (
        (1, 'like'),
        (-1, 'dislike'),
    )

    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction = models.SmallIntegerField(choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.post.pk} : {self.get_reaction_display()}"
