from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "date_joined", "telegram_id",
                  "vk_id", "genshin_uid", "photo", "balance")

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "photo")


class UserStatsSerializer(serializers.Serializer):
    cases_opened = serializers.IntegerField()
    crystals_obtained = serializers.IntegerField()
