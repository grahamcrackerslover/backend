import random
import string

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid
import datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, telegram_id, **kwargs):
        user = self.model(telegram_id=telegram_id, **kwargs)
        user.set_unusable_password()
        user.save()
        return user
    
    
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<timestamp>.jpg
    return 'photos/user_{0}/{1}.jpg'.format(instance.id, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))



class CustomUser(AbstractBaseUser):
    # ID field already exists, no need to write it
    unique_id = models.UUIDField(null=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    telegram_id = models.PositiveBigIntegerField(unique=True, null=True)
    vk_id = models.PositiveBigIntegerField(unique=True, null=True, blank=True)
    vk_access_token = models.TextField(null=True, blank=True)
    genshin_uid = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to=user_directory_path, default='photos/klee.jpeg', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    referrer = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    balance = models.IntegerField(default=0)

    registration_ip = models.GenericIPAddressField(null=True, blank=True)
    current_ip = models.GenericIPAddressField(null=True, blank=True)
    used_ips = models.TextField(default="", blank=True)

    def add_ip(self, new_ip):
        if new_ip not in self.used_ips.split("\n"):
            self.used_ips += f"\n{new_ip}"
            self.save()

    def get_ips(self):
        return self.used_ips.split("\n")

    def ban(self):
        self.is_banned = True
        allowed_punctuation = string.punctuation.replace("\\", "")
        allowed_characters = string.ascii_letters + string.digits + allowed_punctuation
        while True:
            token = "".join(random.choices(allowed_characters, k=64))
            if not self.__class__.objects.filter(token=token).exists():
                self.token = token
                break
        self.save()

    password = models.CharField('password', max_length=128, null=True, blank=True)
    token = models.CharField(max_length=64, unique=True, default="", db_index=True)
    USERNAME_FIELD = 'unique_id'

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} ({self.id})"


@receiver(pre_save, sender=CustomUser)
def create_user_token(sender, instance, *args, **kwargs):
    if not instance.token:
        allowed_punctuation = string.punctuation.replace("\\", "")
        allowed_characters = string.ascii_letters + string.digits + allowed_punctuation
        while True:
            token = "".join(random.choices(allowed_characters, k=64))
            if not CustomUser.objects.filter(token=token).exists():
                instance.token = token
                break
