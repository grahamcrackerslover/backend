from django.db import models

from cases.models import Case, Item
from custom_user.models import CustomUser


class HistoryItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    is_sold = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)
    from_shop = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name


class HistoryCase(models.Model):
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True)
    item = models.OneToOneField(HistoryItem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    opened_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return self.case.name
