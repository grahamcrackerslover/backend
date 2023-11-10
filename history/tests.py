import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHistory:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_live(self, client, test_items_and_cases):
        url = reverse("history-live")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]["items"]) == 10

    def test_user_history(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url = reverse("history-personal")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]["history"]) == 12

    def test_sell_item(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url = reverse("history-sell-item")
        response = client.post(url, {"ids": [test_items_and_cases[0].id]})

        assert response.status_code == status.HTTP_200_OK
