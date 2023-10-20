import asyncio
import random
from django.db import models
from django.utils import timezone
from custom_user.models import CustomUser
from cases.models import Item
from misc.giveaway_permission_bot import (
    check_telegram_user_subscription,
    check_user_wallpost,
)


def default_end_time():
    return timezone.now() + timezone.timedelta(hours=24)


class Giveaway(models.Model):
    TYPE_CHOICES = [
        ("normal", "Normal"),
        ("lottery", "Lottery"),
    ]
    title = models.CharField(max_length=255)
    type = models.CharField(choices=TYPE_CHOICES, default="normal", max_length=10)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=default_end_time)
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(
        CustomUser, related_name="participated_giveaways", blank=True
    )
    items = models.ManyToManyField(Item, through="GiveawayItem", blank=True)
    permission_rules = models.ManyToManyField(
        "GiveawayPermissionRule", related_name="giveaways", blank=True
    )
    price = models.IntegerField(default=0)

    def choose_winners(self):
        giveaway_items = GiveawayItem.objects.filter(giveaway=self)
        participants = list(self.participants.all())
        # winners = set()

        if self.type == "normal":
            for giveaway_item in giveaway_items:
                for _ in range(giveaway_item.count):
                    if not participants:
                        break

                    winners = random.choices(
                        participants, k=min(giveaway_items.count, len(participants))
                    )

                    for winner in winners:
                        giveaway_item.winners.add(winner)
                        participants.remove(winner)
                    # winner = random.choice(participants)
                    # winners.add(winner)
                    # # GiveawayWinner.objects.create(giveaway=self, winner=winner, item=giveaway_item.item)
                    # participants.remove(winner)
                giveaway_item.save()

        else:
            lottery_tickets = LotteryTicket.objects.filter(giveaway=self)
            total_tickets = sum(ticket.tickets for ticket in lottery_tickets)
            ticket_probabilities = []

            for ticket in lottery_tickets:
                probability = ticket.tickets / total_tickets
                ticket_probabilities.append((ticket.user, probability))

            participants = [user_prob[0] for user_prob in ticket_probabilities]

            # Choose winners based on their probabilities
            for giveaway_item in giveaway_items:
                if not participants:
                    break

                winners = random.choices(
                    participants,
                    weights=[
                        prob
                        for user, prob in ticket_probabilities
                        if user in participants
                    ],
                    k=min(giveaway_items.count, len(participants)),
                )

                for winner in winners:
                    giveaway_item.winners.add(winner)
                    participants.remove(winner)

                giveaway_item.save()

        # print('Choose winners METHOD RAN')
        self.is_active = False
        self.save()

    def user_meets_permission_rules(self, user):
        for rule in self.permission_rules.all():
            if not rule.user_meets_condition(user):
                return False
        return True


class GiveawayPermissionRule(models.Model):
    RULE_TYPE_CHOICES = [
        ("account_age_days", "Account age in days"),
        ("coins_purchased_week", "Coins purchased in the last week"),
        ("telegram_channel_subscription", "Telegram channel subscription"),
        ("vk_channel_subscription", "VK channel subscription"),
        ("vk_wallpost", "VK wall post"),
    ]
    rule_type = models.CharField(choices=RULE_TYPE_CHOICES, max_length=50)
    value = models.IntegerField(default=0)
    text_value = models.TextField(blank=True)

    def user_meets_condition(self, user):
        if self.rule_type == "account_age_days":
            account_age = (timezone.now() - user.date_joined).days
            return account_age >= self.value
        elif self.rule_type == "telegram_channel_subscription":
            if not user.telegram_id:
                return False
            is_a_member = check_telegram_user_subscription(user.telegram_id)
            print(is_a_member)
            return is_a_member
        elif self.rule_type == "vk_wallpost":
            if not user.vk_id:
                return False
            return check_user_wallpost(
                user.vk_id, user.vk_access_token, self.text_value
            )
        # elif self.rule_type == 'coins_purchased_week':
        #     # Assuming you have a method on CustomUser to get coins purchased in the last week
        #     return user.get_coins_purchased_last_week() >= int(self.value)

        else:
            raise ValueError(f"Unsupported rule type: {self.rule_type}")


class GiveawayItem(models.Model):
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField()
    winners = models.ManyToManyField(CustomUser, related_name="won_items", blank=True)

    class Meta:
        unique_together = ("giveaway", "item")


class LotteryTicket(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    tickets = models.IntegerField(default=1)

    class Meta:
        unique_together = ("user", "giveaway")
