import datetime
import json

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import Orders


@pytest.mark.django_db
class TestReviews:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_create_review(self, client, test_user):
        client.force_authenticate(test_user)

        url = reverse("reviews-create-review")
        response = client.post(url, {"text": "Test review text"})
        assert response.status_code == status.HTTP_201_CREATED
