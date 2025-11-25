from django.contrib import admin
from .models import Profile, Post, PostReaction

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'user', 'created_at')
    search_fields = ('username', 'user__email')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at', 'likes_count', 'dislikes_count')
    search_fields = ('author__username', 'description')


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'reaction', 'created_at')
    search_fields = ('user__username',)
