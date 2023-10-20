from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class UserStatsSerializer(serializers.Serializer):
    cases_opened = serializers.IntegerField()
    case_opened_mora = serializers.IntegerField()
    crystals_obtained = serializers.IntegerField()
