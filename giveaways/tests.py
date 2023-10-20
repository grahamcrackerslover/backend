import datetime
import json

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from giveaways.models import Giveaway


"""
- Normal
    - Participate once (200)
    - Participate multiple times (400)
- Lottery
    - Participate once (200)
    - Participate up to 5 times (200)
    - Participate more than 5 times (400)
    - Check the chances and prices each time
    
- Giveaway doesn't exist
- Not enough money
- Select winners
- Doesn't fit permissions
"""


@pytest.mark.django_db
class TestGiveaways:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def giveaway(self):
        new_giveaway = Giveaway.objects.create(
            type="normal", title="Test Giveaway", price=5
        )

        return new_giveaway
