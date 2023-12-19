import datetime
import hashlib
import hmac
import json
import random
import string

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from custom_user.models import CustomUser
from custom_user.serializers import UserSerializer
from custom_user.views import checkTelegramAuthorization

from config import BOT_TOKEN

@pytest.mark.django_db
class TestCustomUser:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def telegram_data(self, **kwargs):
        def _telegram_data_factory(**kwargs):
            _id = "".join(random.choices(string.digits, k=5))
            auth_data = {
                "id": _id,
                "first_name": "Test",
                "last_name": "User",
                "username": f"test_user_{_id}",
                "photo_url": "https://t.me/i/userpic/320/RBCFzv2-4EHD8JStqhotclYPW37BGH7nWo0INqRiBLU.jpg",
                "auth_date": timezone.now().timestamp(),
            }

            if "exclude_fields" in kwargs:
                for field in kwargs["exclude_fields"]:
                    del auth_data[field]

            data_check_arr = [f"{key}={value}" for key, value in auth_data.items()]
            data_check_arr.sort()
            data_check_string = "\n".join(data_check_arr)
            secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
            gen_hash = hmac.new(
                secret_key,
                msg=data_check_string.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            auth_data["hash"] = gen_hash

            return auth_data

        return _telegram_data_factory

    def test_send_bullshit(self, client):
        url = reverse("custom-user-telegram-auth")
        response = client.post(url, {"bull": "shit"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_account_telegram_valid(self, client, telegram_data):
        url = reverse("custom-user-telegram-auth")
        data = telegram_data()
        response = client.post(url, {"user": data})

        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert CustomUser.objects.filter(telegram_id=data["id"]).exists()

    def test_create_account_telegram_missing_field(self, client, telegram_data):
        url = reverse("custom-user-telegram-auth")
        data = telegram_data(exclude_fields=["last_name"])
        response = client.post(url, {"user": data})

        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert CustomUser.objects.filter(telegram_id=data["id"]).exists()

    def test_create_account_telegram_missing_fields(self, client, telegram_data):
        url = reverse("custom-user-telegram-auth")
        data = telegram_data(exclude_fields=["last_name", "username", "photo_url"])
        response = client.post(url, {"user": data})

        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert CustomUser.objects.filter(telegram_id=data["id"]).exists()

    def test_create_account_telegram_confirmation_failed_stale_data(
        self, client, telegram_data
    ):
        data = telegram_data()
        data["auth_date"] = 0
        verification = checkTelegramAuthorization(data, True)

        assert verification is False

    def test_create_account_telegram_confirmation_failed_non_telegram_data(
        self, client, telegram_data
    ):
        data = telegram_data()
        data["hash"] = "fakehash"
        verification = checkTelegramAuthorization(data, True)

        assert verification is False

    def test_create_telegram_account_with_existing_referrer(
        self, client, telegram_data
    ):
        data_1 = telegram_data()
        data_2 = telegram_data()
        url = reverse("custom-user-telegram-auth")

        client.post(url, {"user": data_1})
        user_1 = CustomUser.objects.get(telegram_id=data_1["id"])

        client.post(url, {"user": data_2, "referrer": user_1.id})
        user_2 = CustomUser.objects.get(telegram_id=data_2["id"])

        assert user_2.referrer == user_1

    def test_create_telegram_account_with_nonexisting_referrer(
        self, client, telegram_data
    ):
        data = telegram_data()
        url = reverse("custom-user-telegram-auth")

        client.post(url, {"user": data, "referrer": 0})
        user = CustomUser.objects.get(telegram_id=data["id"])

        assert user.referrer is None

    # def test_create_account_vk_valid(self):
    #     # TODO: Write test case for creating account via VK with valid data
    #     pass
    #
    # def test_create_account_vk_invalid_id(self):
    #     # TODO: Write test case for creating account via VK with an invalid ID/token
    #     pass
    #
    # def test_create_account_vk_invalid_token(self):
    #     # TODO: Write test case for creating account via VK with an invalid ID/token
    #     pass
