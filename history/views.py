from django.db import transaction
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated

from history.models import HistoryItem, HistoryCase
from history.serializers import HistoryItemSerializer, HistoryCaseSerializer
from misc.responses import success_response, error_response
from orders.models import Orders


@api_view(["GET"])
def live(request):
    # Берем 10 последних кейсов
    items = HistoryCase.objects.all()
    last_10 = items[:10]
    serialized_items = HistoryCaseSerializer(last_10, many=True)

    return success_response(
        heading="",
        message="",
        data={"items": serialized_items.data},
        code=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_history(request):
    # Берем все выпавшие предметы
    items = HistoryItem.objects.filter(owner=request.user)
    serialized_cases = HistoryItemSerializer(items, many=True)

    return success_response(
        heading="",
        message="",
        data={"history": serialized_cases.data},
        code=status.HTTP_200_OK
    )


@api_view(["POST"])
def sell_items(request):
    # Получаем список ID предметов
    item_ids = request.data["ids"]  # This should be a list of item IDs.

    # Проверка, что item_ids является списком
    if not isinstance(item_ids, list):
        return error_response(
            heading="Неверный формат данных",
            message="Должен быть предоставлен список ID предметов.",
            errors=["not_a_list"],
            code=status.HTTP_400_BAD_REQUEST
        )

    sold_items = []
    total_price = 0
    errors = []

    with transaction.atomic():
        for item_id in item_ids:
            item = HistoryItem.objects.filter(id=item_id, owner=request.user).first()

            if not item:
                errors.append({"id": item_id, "error": "Item not found or not owned by user"})
                continue

            if item.from_shop:
                errors.append({"id": item_id, "error": "Item from shop cannot be sold"})
                continue

            if item.is_sold:
                errors.append({"id": item_id, "error": "Item is already sold"})
                continue

            if Orders.objects.filter(item=item).exists():
                errors.append({"id": item_id, "error": "Item is ordered and cannot be sold"})
                continue

            # Продажа предмета
            item.is_sold = True
            total_price += item.item.price
            sold_items.append(item)

        # Если есть предметы для продажи
        if sold_items:
            # Обновляем баланс пользователя и сохраняем изменения для каждого предмета
            request.user.balance += total_price
            request.user.save()
            for item in sold_items:
                item.save()

        # Если есть ошибки, возвращаем их
        if errors:
            return error_response(
                heading="Ошибка при продаже предметов",
                message="Некоторые предметы не могут быть проданы.",
                errors=errors,
                code=status.HTTP_400_BAD_REQUEST
            )

        # Если все предметы проданы успешно
        return success_response(
            heading="Предметы проданы",
            message=f"Получено {total_price} моры за продажу предметов.",
            data={"sold_items": [item.id for item in sold_items], "total_price": total_price},
            code=status.HTTP_200_OK
        )