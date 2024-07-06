# 상대경로: Django4/community/board/serializers.py

from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.profile.nickname', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'nickname', 'title', 'body', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='user.profile.nickname', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'nickname', 'comment', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }
