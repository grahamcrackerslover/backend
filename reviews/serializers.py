from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "is_positive", "text", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")
