from rest_framework import serializers

from cases.serializers import ItemSerializer
from custom_user.serializers import BasicUserSerializer
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    owner = BasicUserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'item', 'amount', 'owner', 'created', 'currency']
