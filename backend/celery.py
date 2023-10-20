# your_project/celery.py

from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from celery import Celery
from django.conf import settings
from logging.config import dictConfig

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# dictConfig(settings.LOGGING)

app.conf.beat_schedule = {
    "select-winners-every-5-minutes": {
        "task": "giveaways.tasks.select_winners",
        "schedule": timedelta(minutes=5),
    },
}
