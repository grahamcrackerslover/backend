from rest_framework import serializers

from history.serializers import HistoryItemSerializer
from .models import Orders


class OrdersSerializer(serializers.ModelSerializer):
    item = HistoryItemSerializer

    class Meta:
        model = Orders
        exclude = ("is_test_instance",)
