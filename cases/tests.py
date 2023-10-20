import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cases.models import Case, Item, CaseItem


@pytest.mark.django_db
class TestCase:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def test_item(self):
        item = Item.objects.create(
            name="Test Item", type="crystal", crystals=1, price=100, cashback=None
        )
        return item

    @pytest.fixture
    def test_case(self, test_item):
        case = Case.objects.create(name="Test Case", photo_url="", price=50)
        case_item = CaseItem.objects.create(case=case, item=test_item, drop_rate=100)
        return case

    def test_open_case(self, client, test_user, test_case):
        client.force_authenticate(user=test_user)

        assert test_user.balance >= Case.objects.get(id=test_case.pk).price

        url = reverse("cases-open-case", kwargs={"pk": test_case.pk})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK

    def test_open_case_insufficient_balance(self, client, test_user, test_case):
        client.force_authenticate(user=test_user)

        test_user.balance = 0
        test_user.save()
        assert test_user.balance < Case.objects.get(id=test_case.pk).price

        url = reverse("cases-open-case", kwargs={"pk": test_case.pk})
        response = client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_open_nonexistent_case(self, client, test_user, test_case):
        client.force_authenticate(user=test_user)

        url = reverse("cases-open-case", kwargs={"pk": 999})
        response = client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
