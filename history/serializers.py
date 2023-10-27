# serializers.py
from rest_framework import serializers

from cases.serializers import ItemSerializer
from .models import HistoryItem, HistoryCase


class HistoryItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = HistoryItem
        fields = "__all__"


class HistoryCaseSerializer(serializers.ModelSerializer):
    item = HistoryItemSerializer()

    class Meta:
        model = HistoryCase
        fields = "__all__"
