from rest_framework import serializers

from .models import Item, Case


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ("id", "name", "description", "price", "for_sale", "photo_url")

    def create(self, validated_data):
        item = Item.objects.create(
            name=validated_data["name"],
            type=validated_data["type"],
            crystals=validated_data["crystals"],
            price=validated_data["price"],
        )
        return item


class CaseSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Case
        fields = "__all__"
