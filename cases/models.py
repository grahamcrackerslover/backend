from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from custom_user.models import CustomUser

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    photo_url = models.ImageField(upload_to="items/")
    TYPE_CHOICES = [("crystal", "Crystal"), ("moon", "Moon"), ("money", "Money")]
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    crystals = models.BigIntegerField()
    price = models.IntegerField()
    sgd_price = models.IntegerField(default=0)
    for_sale = models.BooleanField(default=True)
    cashback = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Case(models.Model):
    CATEGORY_CHOICES = [
        ("mondstadt", "Мондштадт"),
        ("liyue", "Ли Юэ"),
        ("sumeru", "Сумеру"),
        ("inadzuma", "Инадзума"),
        ("special", "Специальные"),
    ]
    name = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, default="mondstadt", max_length=10)
    photo_url = models.ImageField(upload_to="cases/")
    items = models.ManyToManyField(Item, through="CaseItem", blank=True)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class CaseItem(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    drop_rate = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.item.name} in {self.case.name}"
