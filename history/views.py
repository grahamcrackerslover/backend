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
def sell_item(request):
    # Получаем ID предмета
    item_id = request.data["id"]
    # Ищем предмет с указанным ID, принадлежащий пользователю
    item = HistoryItem.objects.filter(id=item_id, owner=request.user).first()

    # Если предмет найден
    if item:
        # Если предмет куплен в магазине, его нельзя продать
        if item.from_shop:
            return error_response(
                heading="Предмет из магазина",
                message="К сожалению, Вы не можете продать предмет, который был куплен в магазине",
                errors=["sell_item_from_shop"],
                code=status.HTTP_400_BAD_REQUEST
            )
        # Если предмет уже продан
        elif item.is_sold:
            return error_response(
                heading="Предмет уже продан",
                message="К сожалению, Вы не можете продать предмет, который уже был продан. Если Вы считаете, что это "
                        "ошибка, обратитесь к поддержку",
                errors=["item_already_sold"],
                code=status.HTTP_400_BAD_REQUEST
            )
        # Если на предмет уже создан заказ
        elif Orders.objects.filter(item=item).exists():
            return error_response(
                heading="Предмет заказан",
                message="К сожалению, Вы не можете продать предмет, который уже заказан. Для начала отмените заказ",
                errors=["sell_ordered_item"],
                code=status.HTTP_400_BAD_REQUEST
            )
        # Если все условия выполнены
        else:
            # Устанавливаем атрибут is_sold у предмета в True, чтобы не удалять его из БД
            # и добавляем сумму продажи предмета на баланс пользователя
            item.is_sold = True
            request.user.balance += item.item.price
            request.user.save()
            item.save()
            return success_response(
                heading="Предмет продан",
                message=f"Получено {item.item.price} моры",
                data={},
                code=status.HTTP_200_OK
            )

    # Если предмет не найден
    return error_response(
        heading="Предмет не существует",
        message="К сожалению, этот предмет не существует, или Вы не его владелец. Если Вы считаете, что это "
                "ошибка, обратитесь к поддержку",
        errors=["item_not_exists"],
        code=status.HTTP_400_BAD_REQUEST
    )
