# serializers.py
from rest_framework import serializers
from .models import HistoryItem, HistoryCase


class HistoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryItem
        fields = "__all__"


class HistoryCaseSerializer(serializers.ModelSerializer):
    item = HistoryItemSerializer()

    class Meta:
        model = HistoryCase
        fields = "__all__"
