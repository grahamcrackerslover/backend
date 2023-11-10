from rest_framework import serializers

from custom_user.serializers import BasicUserSerializer
from .models import Review, Reply


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ("id", "name", "text", "created_at")
        read_only_fields = ("id", "created_at")


class ReviewSerializer(serializers.ModelSerializer):
    author = BasicUserSerializer(read_only=True)
    reply = ReplySerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "is_positive", "text", "author", "created_at", "reply")
        read_only_fields = ("id", "author", "created_at")
