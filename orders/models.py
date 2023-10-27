import asyncio
import logging

from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from history.models import HistoryItem as HItem
from misc.order_notifier_bot import send_order_notification
import misc


class Orders(models.Model):
    STEP_CHOICES = [
        ("processing", "Processing"),
        ("withdrawing", "Withdrawing"),
        ("withdrawn", "Withdrawn"),
    ]
    id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(HItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    step = models.CharField(
        choices=STEP_CHOICES, default="processing", max_length=11, null=True
    )
    is_cancelled = models.BooleanField(default=False)
    is_allowed = models.BooleanField(default=True)
    genshin_uid = models.PositiveBigIntegerField()

    is_in_queue = models.BooleanField(default=False)
    is_test_instance = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.item} for {self.item.owner.first_name}. Step: {self.step}"


class Wallet(models.Model):
    id = models.BigAutoField(primary_key=True)  # wallet id, assume = 0 for PH wallet
    wallet_address = models.TextField()
    default_payment = models.IntegerField(default=100)  # amount of money in USDT TODO: CHANGE TO 500

    def get_balance_sgd(self):
        pass

    def get_balance_usdt(self):
        pass


# @receiver(post_save, sender=Orders)
# def send_order_after_create(sender, instance, created, **kwargs):
#     with transaction.atomic():
#         if instance.is_test_instance:
#             return
#         if created:
#             if Orders.objects.filter(is_in_queue=True).count() < 10:
#                 instance.is_in_queue = True
#                 instance.save()
#
#                 wallet = Wallet.objects.get(id=0)
#                 queue_price = Orders.objects.filter(is_in_queue=True).aggregate(Sum('item__ph_price'))['item__ph_price__sum']
#                 money_left = wallet.total_balance
#                 difference = queue_price - money_left
#                 if difference >= 0:
#                     money_to_send = wallet.default_payment
#                     if difference > money_to_send:
#                         money_to_send += difference - money_to_send
#
#                     wallet.total_balance += money_to_send
#                     wallet.save()
#                     # TODO: Send money to the seller and a notification in the bot
#
#                 misc.wittebane.send_order(instance)
