import datetime
import hashlib
import hmac
import time

import requests
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated

from config import BOT_TOKEN
from giveaways.models import Giveaway, GiveawayItem, LotteryTicket
from history.models import HistoryCase as HCase
from history.models import HistoryItem as HItem
from history.serializers import HistoryItemSerializer as HItemSerializer
from misc.responses import error_response, success_response
from .models import CustomUser
from .serializers import UserSerializer


def merge_accounts(first: CustomUser, second: CustomUser):
    # Сохраняется first, удаляется second
    # То есть сохраняем тот, К КОТОРОМУ ПРИВЯЗЫВАЮТ
    # и удаляем тот, КОТОРЫЙ ПРИВЯЗЫВАЮТ

    # Меняем каждое поле каждого связанного инстанса
    related_hitems = HItem.objects.filter(owner=second)
    related_hitems.update(owner=first)

    related_hcases = HCase.objects.filter(user=second)
    related_hcases.update(user=first)

    related_lottery_tickets = LotteryTicket.objects.filter(user=second)
    related_lottery_tickets.update(user=first)

    # То же самое для many-to-many моделей
    related_giveaways = Giveaway.objects.filter(participants__in=[second])
    for rel_giv in related_giveaways:
        rel_giv.participants.remove(second)
        rel_giv.participants.add(first)

    related_giveaway_items = GiveawayItem.objects.filter(winners__in=[second])
    for rel_giv_item in related_giveaway_items:
        rel_giv_item.winners.remove(second)
        rel_giv_item.winners.add(first)

    # Объединяем юзеров
    second_serialized = UserSerializer(second).data
    second.delete()

    first.vk_id = first.vk_id if first.vk_id else second.vk_id
    first.telegram_id = first.telegram_id if first.telegram_id else second.telegram_id
    first.genshin_uid = first.genshin_uid if first.genshin_uid else second.genshin_uid
    first.is_frozen = (
        True if second_serialized["is_frozen"] or first.is_frozen else False
    )
    first.balance = first.balance + second_serialized["balance"]
    first.referrer = first.referrer if first.referrer else second.referrer
    first.used_ips = "\n".join(
        set(first.used_ips.split("\n") + second_serialized["used_ips"].split("\n"))
    )
    first.save()


def checkTelegramAuthorization(tg_user):
    # Подтверждение данных путем сравнения хэшированной строки из всех отсортированных
    # полей (кроме поля хэша) и самого хэша
    check_hash = tg_user["hash"]
    auth_data = tg_user.copy()
    del auth_data["hash"]
    data_check_arr = [f"{key}={value}" for key, value in auth_data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
    hash = hmac.new(
        secret_key, msg=data_check_string.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()
    if not constant_time_compare(hash, check_hash):
        return False
    if (time.time() - tg_user["auth_date"]) > 86400:
        return False
    return True


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def telegram_auth(request):
    # Если уже аутентифицирован (в хедерах есть квт)
    if isinstance(request.user, CustomUser):
        # Если оба аккаунта привязаны
        if request.user.telegram_id is not None and request.user.vk_id is not None:
            return error_response(
                heading="Аккаунты уже привязаны!",
                message="Кажется, аккаунты уже связаны друг с другом, так что делать это заново не надо",
                errors=["accounts_already_linked"],
                code=status.HTTP_400_BAD_REQUEST
            )
        # Если привязан вк и не привязан тг
        if request.user.telegram_id is None and request.user.vk_id is not None:
            # Если юзера с таким айди тг не существует
            if not CustomUser.objects.filter(telegram_id=request.data["id"]).exists():
                # Привязать аккаунты
                request.user.telegram_id = request.data["id"]
                request.user.save()
                return success_response(
                    heading="Аккаунты привязаны!",
                    message="Аккаунты успешно привязаны, поздравляем!",
                    data={},
                    code=status.HTTP_200_OK
                )
            else:
                # Если такой юзер все таки существует, объединить аккаунты
                merge_accounts(
                    CustomUser.objects.get(telegram_id=request.data["id"]), request.user
                )
                return success_response(
                    heading="Аккаунты совмещены!",
                    message="Кажется, пользователь с таким привязанным аккаунтом уже существует, поэтому мы"
                            " соединили аккаунты в один",
                    data={},
                    code=status.HTTP_200_OK
                )

    data = request.data.get("user")
    referrer = request.data.get("referrer")  # Если передан реферер

    # Если есть данные и они верны
    if data and checkTelegramAuthorization(data):
        # Взять или создать аккаунт с таким айди
        user, created = CustomUser.objects.get_or_create(
            telegram_id=data["id"],
        )

        user_ip = request.META.get("REMOTE_ADDR")  # Взять айпи юзера
        if created:
            if referrer:
                try:
                    user.referrer = CustomUser.objects.get(id=referrer)
                except CustomUser.DoesNotExist:
                    pass

            user.registration_ip = user_ip

        # Обновить поля (не важно залогинен или зареган)
        user.last_login = timezone.now()
        user.first_name = data["first_name"]
        user.last_name = data.get("last_name")
        user.photo_url = data.get("photo_url")
        user.current_ip = user_ip
        user.add_ip(user_ip)

        # Сохранить изменения
        user.save()

        # Сереализровать в жсон
        user_json = UserSerializer(user)

        # Заменить код на 201 если создан, иначе 201
        response_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return success_response(
            heading="",
            message="",
            data={"user": user_json.data, "token": user.token},
            code=response_code
        )
    # Если данных нет или они не прошли проверку
    raise NotAuthenticated()


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def vk_auth(request):
    # Тот же принцип, что в авторизации тг
    if isinstance(request.user, CustomUser):
        if request.user.telegram_id is not None and request.user.vk_id is not None:
            return error_response(
                heading="Аккаунты уже привязаны!",
                message="Кажется, аккаунты уже связаны друг с другом, так что делать это заново не надо",
                errors=["accounts_already_linked"],
                code=status.HTTP_400_BAD_REQUEST
            )
        if request.user.telegram_id is not None and request.user.vk_id is None:
            if not CustomUser.objects.filter(vk_id=request.data["userId"]).exists():
                request.user.vk_id = request.data["userId"]
                request.user.save()
                return success_response(
                    heading="Аккаунты привязаны!",
                    message="Аккаунты успешно привязаны, поздравляем!",
                    data={},
                    code=status.HTTP_200_OK
                )
            else:
                merge_accounts(
                    CustomUser.objects.get(vk_id=request.data["userId"]), request.user
                )
                return success_response(
                    heading="Аккаунты совмещены!",
                    message="Кажется, пользователь с таким привязанным аккаунтом уже существует, поэтому мы"
                            " соединили аккаунты в один",
                    data={},
                    code=status.HTTP_200_OK
                )

    user_id = request.data["userId"]
    access_token = request.data["accessToken"]
    referrer = request.data.get("referrer")

    payload = {
        "user_id": user_id,
        "access_token": access_token,
        "fields": ["photo_100"],
        "v": "5.131",
    }

    # Делается запрос к апи вк, для получения данных юзера
    req = requests.get(f"https://api.vk.com/method/users.get", params=payload)
    if not req.status_code == 200:  # Если запрос не прошел
        return error_response(
            heading="Ошибка",
            message="У нас возникли проблемы с верификацией данных. Если Вы считаете, что это ошибка",
            errors=["accounts_already_linked"],
            code=status.HTTP_400_BAD_REQUEST
        )
    data = req.json()
    if (
        "response" not in data
    ):  # Если в дате нет поля респонс (такое бывает, даже если запрос прошел)
        return error_response(
            heading="Ошибка",
            message="У нас возникли проблемы с верификацией данных. Если Вы считаете, что это ошибка",
            errors=["accounts_already_linked"],
            code=status.HTTP_400_BAD_REQUEST
        )

    user_details = data["response"][0]
    # То же, что и в тг авторизации
    user, created = CustomUser.objects.get_or_create(
        vk_id=user_details["id"],
    )
    user_ip = request.META.get("REMOTE_ADDR")
    if created:
        if referrer:
            try:
                user.referrer = CustomUser.objects.get(id=referrer)
            except CustomUser.DoesNotExist:
                pass

        user.registration_ip = user_ip

    user.last_login = datetime.datetime.now()
    user.first_name = user_details["first_name"]
    user.last_name = user_details.get("last_name")
    user.photo_url = user_details["photo_100"]
    user.vk_access_token = request.data["accessToken"]
    user.current_ip = user_ip
    user.add_ip(user_ip)

    user.save()

    user_json = UserSerializer(user)
    response_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return success_response(
        heading="",
        message="",
        data={"user": user_json.data, "token": user.token},
        code=response_code
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def details(request):
    # Получаем данные юзера
    user_json = UserSerializer(request.user)
    return success_response(
        heading="",
        message="",
        data={"user": user_json.data},
        code=status.HTTP_200_OK
    )


@api_view(["GET"])
def basic_details(request):
    user_id = request.data['user_id']
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return error_response(
            heading="Ошибка",
            message="Пользователь не существует",
            errors=["user_not_exists"]
        )
    return success_response(
        heading="",
        message="",
        data={"user": serialized_data},
        code=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inventory(request):
    # Фильтруем выпавшие предметы (у них своя модель) по юзеру
    items = HItem.objects.filter(owner=request.user)
    serialized_items = HItemSerializer(items, many=True)

    return success_response(
        heading="",
        message="",
        data={"items": serialized_items},
        code=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def set_uid(request):
    # Устанавливаем юид как дефолтный для юзера
    # TODO: добавить обработчик ошибок, для таких случаев как неверный формат юид
    genshin_uid = request.data["genshin_uid"]
    user = request.user
    user.genshin_uid = genshin_uid
    user.save()

    return success_response(
        heading="UID установлен",
        message="Теперь он будет использоваться по умолчанию при покупках и выводах, но Вы все еще сможете"
                " сменить его вручную",
        data={},
        code=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats(request):
    # Берем все предметы, полученные юзером
    cases_opened = HItem.objects.filter(owner=request.user)
    # Фильтруем данные: сколько открыто кейсов, на какую сумму и сколько кристаллов выбито
    user_stats = {
        "cases_opened": cases_opened.count(),
        "case_opened_mora": cases_opened.aggregate(total=Sum("price"))["total"],
        "crystals_obtained": cases_opened.aggregate(total=Sum("crystals"))["total"],
    }
    user_stats["case_opened_mora"] = user_stats["case_opened_mora"] if user_stats["case_opened_mora"] else 0
    user_stats["crystals_obtained"] = user_stats["crystals_obtained"] if user_stats["crystals_obtained"] else 0

    return success_response(
        heading="",
        message="",
        data={"stats": user_stats},
        code=status.HTTP_200_OK
    )
