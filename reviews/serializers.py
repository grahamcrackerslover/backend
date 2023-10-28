from rest_framework import serializers

from custom_user.serializers import BasicUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author = BasicUserSerializer()

    class Meta:
        model = Review
        fields = ("id", "is_positive", "text", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")
