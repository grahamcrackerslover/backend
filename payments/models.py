import random
import string

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

import custom_user.models
from cases.models import Item
from custom_user.models import CustomUser
from history.models import HistoryItem as HItem


class Code(models.Model):
    code = models.CharField(max_length=255, unique=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    uses = models.IntegerField(default=-1)

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                new_code = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                if not self.__class__.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        abstract = True


class BonusCode(Code):
    ITEM = "item"
    MONEY = "money"
    PROMO_TYPE_CHOICES = [
        (ITEM, "item"),
        (MONEY, "money"),
    ]

    promo_type = models.CharField(max_length=10, choices=PROMO_TYPE_CHOICES)
    amount = models.SmallIntegerField(null=True, blank=True)
    items = models.ManyToManyField(Item, blank=True)

    def apply(self, user):
        if self.uses == -1 or self.uses > 0:
            if self.promo_type == "item":
                for item_info in self.items.all():
                    new_item = HItem.objects.create(
                        name=item_info.name,
                        type=item_info.type,
                        crystals=item_info.crystals,
                        price=item_info.price,
                        owner=user,
                    )
                    new_item.save()
            else:
                user.balance += self.amount
                user.save()

            self.uses -= 1 if self.uses > 0 else 0
            self.save()
            return True

        return False


class PromoCode(Code):
    # amount = models.SmallIntegerField(null=True, blank=True)
    percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True
    )

    def apply(self, amount):
        if self.uses == -1 or self.uses > 0:
            self.uses -= 1 if self.uses > 0 else 0
            self.save()
            return amount + amount * self.percentage / 100

        return False


class Payment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField()
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3)
