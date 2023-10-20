from django.db import models
from django.utils import timezone

from custom_user.models import CustomUser


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    is_positive = models.BooleanField(default=True)
    text = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.first_name}'s Review"


class Reply(models.Model):
    id = models.AutoField(primary_key=True)
    review = models.OneToOneField(
        Review, on_delete=models.CASCADE, related_name="reply"
    )
    name = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reply to {self.review.author.first_name}'s Review"
