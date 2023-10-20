from rest_framework import serializers

from cases.serializers import ItemSerializer
from custom_user.models import CustomUser
from custom_user.serializers import UserSerializer
from .models import Giveaway, GiveawayItem, LotteryTicket


class LotteryTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotteryTicket
        fields = ["user", "giveaway", "tickets"]


class GiveawayParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "photo_url")


class GiveawayItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    winners = GiveawayParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = GiveawayItem
        fields = ("item", "count", "winners")


# class GiveawayWinnerSerializer(serializers.ModelSerializer):
#     winner = GiveawayParticipantSerializer()
#
#     class Meta:
#         model = GiveawayWinner
#         fields = ('winner', 'item')
#


class GiveawaySerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    items = GiveawayItemSerializer(source="giveawayitem_set", many=True, read_only=True)
    type = serializers.ChoiceField(choices=Giveaway.TYPE_CHOICES)

    class Meta:
        model = Giveaway
        # fields = '__all__'
        exclude = ("permission_rules",)
