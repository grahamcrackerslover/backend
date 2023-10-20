import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import Orders


@pytest.mark.django_db
class TestOrders:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_create_order(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url = reverse("orders-create-order")
        response = client.post(
            url,
            {
                "id": test_items_and_cases[0].id,
                "genshin_uid": 777777777,
                "is_test_instance": True,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_order_exists(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url = reverse("orders-create-order")
        response_1 = client.post(
            url,
            {
                "id": test_items_and_cases[0].id,
                "genshin_uid": 777777777,
                "is_test_instance": True,
            },
        )
        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = client.post(
            url,
            {
                "id": test_items_and_cases[0].id,
                "genshin_uid": 777777777,
                "is_test_instance": True,
            },
        )
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_item_doesnt_exist(self, client, test_user):
        client.force_authenticate(test_user)

        url = reverse("orders-create-order")
        response = client.post(
            url, {"id": 999, "genshin_uid": 777777777, "is_test_instance": True}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_order(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url_1 = reverse("orders-create-order")
        url_2 = reverse("orders-cancel-order")
        response_1 = client.post(
            url_1,
            {
                "id": test_items_and_cases[0].id,
                "genshin_uid": 777777777,
                "is_test_instance": True,
            },
        )
        assert response_1.status_code == status.HTTP_201_CREATED

        response_2 = client.post(url_2, {"id": response_1.data['data']['id']})
        assert response_2.status_code == status.HTTP_200_OK

    def test_cancel_order_doesnt_exist(self, client, test_user):
        client.force_authenticate(test_user)

        url = reverse("orders-cancel-order")
        response = client.post(url, {"id": 999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cancel_order_on_withdrawal(self, client, test_user, test_items_and_cases):
        client.force_authenticate(test_user)

        url_1 = reverse("orders-create-order")
        response = client.post(
            url_1,
            {
                "id": test_items_and_cases[0].id,
                "genshin_uid": 777777777,
                "is_test_instance": True,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

        order = Orders.objects.get(id=response.data['data']['id'])
        order.step = "withdrawing"
        order.save()

        url_2 = reverse("orders-cancel-order")
        response_2 = client.post(url_2, {"id": response.data['data']['id']})
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
