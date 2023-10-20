from celery import shared_task

import config
from .models import Giveaway
from django.utils import timezone
import logging
import requests

logger = logging.getLogger(__name__)


@shared_task
def select_winners():
    logger.debug("Starting the select_winners task")

    giveaways = Giveaway.objects.filter(end_time__lte=timezone.now(), is_active=True)
    logger.debug(f"Found {giveaways.count()} giveaways in total")

    for giveway in giveaways:
        logger.debug(f"Processing giveaway: {giveway.title} (ID: {giveway.pk})")
        giveway.choose_winners()

    logger.debug("Finished the select_winners task")


@shared_task
def check_balance_sgd():
    retries = 5
    while retries > 0:
        response = requests.post(
            "https://dev.api.elitedias.com/elitedias_api_balance",
            headers={'Origin': 'dev.api.elitedias.com'},
            json={'api_key': config.API_KEY},
            timeout=60
        ).json()
        if response["code"] != "200":
            retries -= 0
        else:
            return response["reseller_balance"]

    # TODO: implement critical error log
    return False


@shared_task
def check_balance_usdt():
    pass
