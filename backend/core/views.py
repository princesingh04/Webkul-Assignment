# core/views.py
from django.db import transaction
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers_auth import SignupSerializer, LoginSerializer
from .serializers import ProfileSerializer, PostSerializer
from .models import Profile, Post, PostReaction


class SignupView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # IMPORTANT: no JWT/Session auth here

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "User registered successfully",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # IMPORTANT: no JWT/Session auth here

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/profile/   -> current user's profile
    PATCH /api/profile/   -> update current user's profile
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/posts/   -> list all posts (global feed)
    POST /api/posts/   -> create post (image + description)
    """
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}


class PostDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/posts/<id>/  -> delete only your own post
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author != self.request.user.profile:
            # you can use DRF's PermissionDenied, but this is fine for now
            return Response(
                {"detail": "You can only delete your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()


class PostReactView(APIView):
    """
    POST /api/posts/<pk>/react/
    body: { "reaction": "like" } or { "reaction": "dislike" }

    Behaviour:
    - no existing reaction -> create one
    - same reaction again  -> remove reaction (toggle off)
    - opposite reaction    -> switch like <-> dislike
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            with transaction.atomic():
                post = Post.objects.select_for_update().get(pk=pk)
                profile = request.user.profile

                reaction_str = request.data.get("reaction")
                if reaction_str not in ("like", "dislike"):
                    return Response(
                        {"detail": "reaction must be 'like' or 'dislike'"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                new_value = 1 if reaction_str == "like" else -1

                existing = PostReaction.objects.filter(
                    user=profile, post=post
                ).first()

                # case 1: no reaction yet -> create one
                if existing is None:
                    PostReaction.objects.create(
                        user=profile, post=post, reaction=new_value
                    )
                    if new_value == 1:
                        Post.objects.filter(pk=post.pk).update(
                            likes_count=F("likes_count") + 1
                        )
                    else:
                        Post.objects.filter(pk=post.pk).update(
                            dislikes_count=F("dislikes_count") + 1
                        )

                # case 2: same reaction -> remove it (toggle off)
                elif existing.reaction == new_value:
                    if existing.reaction == 1:
                        Post.objects.filter(pk=post.pk).update(
                            likes_count=F("likes_count") - 1
                        )
                    else:
                        Post.objects.filter(pk=post.pk).update(
                            dislikes_count=F("dislikes_count") - 1
                        )
                    existing.delete()

                # case 3: opposite reaction -> switch
                else:
                    if existing.reaction == 1:
                        # previously liked, now dislike
                        Post.objects.filter(pk=post.pk).update(
                            likes_count=F("likes_count") - 1,
                            dislikes_count=F("dislikes_count") + 1,
                        )
                    else:
                        # previously disliked, now like
                        Post.objects.filter(pk=post.pk).update(
                            dislikes_count=F("dislikes_count") - 1,
                            likes_count=F("likes_count") + 1,
                        )
                    existing.reaction = new_value
                    existing.save(update_fields=["reaction", "updated_at"])

                # refresh post with updated counters
                post.refresh_from_db()

        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
