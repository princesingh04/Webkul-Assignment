from rest_framework import serializers
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Profile, Post, PostReaction

# --- Helpers ---
ALLOWED_IMAGE_TYPES = ("image/jpeg", "image/png")
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image_file(file):
    content_type = getattr(file, "content_type", None)
    size = getattr(file, "size", None)

    if content_type is None or size is None:
        raise ValidationError(_("Uploaded file is invalid."))

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(_("Unsupported image type. Allowed: JPEG, PNG."))

    if size > MAX_IMAGE_SIZE:
        raise ValidationError(_("Image too large. Max size is 5 MB."))


# --- Serializers ---
class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "user_email",
            "bio",
            "location",
            "phone",
            "profile_image",
            "date_of_birth",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user_email", "created_at", "updated_at")

    def validate_profile_image(self, file):
        if file:
            validate_image_file(file)
        return file


class PostReactionSerializer(serializers.ModelSerializer):
    # Accept 'like'/'dislike' strings on input
    reaction = serializers.ChoiceField(choices=("like", "dislike"))

    class Meta:
        model = PostReaction
        fields = ("id", "user", "post", "reaction", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "user")

    def to_internal_value(self, data):
        # Convert 'like'/'dislike' to 1/-1 before validation/storage
        if "reaction" in data and isinstance(data["reaction"], str):
            if data["reaction"].lower() == "like":
                data["reaction"] = 1
            elif data["reaction"].lower() == "dislike":
                data["reaction"] = -1
        return super().to_internal_value(data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["reaction"] = "like" if instance.reaction == 1 else "dislike"
        return rep


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    image = serializers.ImageField(required=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_id",
            "image",
            "description",
            "likes_count",
            "dislikes_count",
            "user_reaction",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "likes_count", "dislikes_count", "created_at", "updated_at")

    def validate_image(self, file):
        if file:
            validate_image_file(file)
        return file

    def get_user_reaction(self, obj):
        request = self.context.get("request", None)
        if request is None or not request.user.is_authenticated:
            return None
        # the Profile object may not exist for the user (ensure it does)
        try:
            profile = request.user.profile
        except Exception:
            return None
        reaction_obj = obj.reactions.filter(user=profile).first()
        if not reaction_obj:
            return None
        return "like" if reaction_obj.reaction == 1 else "dislike"

    def create(self, validated_data):
        """
        Set author from context (expects request.user.profile to exist).
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to create a post.")

        try:
            profile = request.user.profile
        except Exception:
            raise serializers.ValidationError("Profile not found for current user.")

        validated_data["author"] = profile
        return super().create(validated_data)
