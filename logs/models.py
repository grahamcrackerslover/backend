from django.db import models
from django.utils import timezone

from custom_user.models import CustomUser


# Create your models here.
class Log(models.Model):
    LOG_TYPES = (
        ('SYSTEM', 'System'),
        ('DEBUG', 'Debug'),
        ('INFO', 'Information'),
        ('WARN', 'Warning'),
        ('ERROR', 'Error'),
    )
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=20, choices=LOG_TYPES)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    request_url = models.URLField(max_length=2000, null=True, blank=True)
    http_method = models.CharField(max_length=10, null=True, blank=True)
    response_status_code = models.PositiveSmallIntegerField(default=200)
    error_details = models.CharField(max_length=200)
    additional = models.CharField(max_length=200)

    @classmethod
    def system(cls, **kwargs):
        log = cls(type='SYSTEM', **kwargs)
        log.save()

    @classmethod
    def debug(cls, **kwargs):
        log = cls(type='DEBUG', **kwargs)
        log.save()

    @classmethod
    def info(cls, **kwargs):
        log = cls(type='INFO', **kwargs)
        log.save()

    @classmethod
    def warn(cls, **kwargs):
        log = cls(type='WARN', **kwargs)
        log.save()

    @classmethod
    def error(cls, **kwargs):
        log = cls(type='ERROR', **kwargs)
        log.save()

        # Send message to admins

    def save(self, *args, **kwargs):
        if not self.id:
            self.timestamp = timezone.now()
        return super(Log, self).save(*args, **kwargs)

    def __str__(self):
        return f"[{self.timestamp}] ({self.type}) - {self.action}"
