from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "date_joined", "telegram_id", "vk_id", "genshin_uid", "photo_url",
                  "is_verified", "balance")


class UserStatsSerializer(serializers.Serializer):
    cases_opened = serializers.IntegerField()
    case_opened_mora = serializers.IntegerField()
    crystals_obtained = serializers.IntegerField()


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "photo_url")
