from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated

from history.models import HistoryItem as HItem
from misc.responses import error_response, success_response
from payments.models import Payment
from .models import Orders


def place_order(item, genshin_uid, payment=None, is_test_instance=False):
    # Устанавливаем параметр is_ordered для предмета и сохраняем
    item.is_ordered = True
    item.save()

    # Создаем ордер
    order = Orders.objects.create(
        item=item, genshin_uid=genshin_uid, is_test_instance=is_test_instance
    )

    return success_response(
        heading="Заказ создан",
        message=f"Вы успешно создали заказ на \"{item.item.name}\"!",
        data={'order_id': order.id, 'payment_id': payment.id if payment else None},
        code=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    genshin_uid = request.data["genshin_uid"]
    item_id = request.data["id"]

    # Проверяем UID на валидность
    if not genshin_uid or len(str(genshin_uid)) != 9 or str(genshin_uid)[0] not in "6789":
        return error_response(
            heading="Неверный UID",
            message="Кажется, Вы указали неверный UID. Если Вы считаете, что это ошибка, обратитесь в поддержку",
            errors=["incorrect_uid"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Получаем предмет, принадлежащий пользователю
    item = HItem.objects.filter(owner=request.user, id=item_id).first()
    if not item:
        return error_response(
            heading="Предмет не существует",
            message="К сожалению, этот предмет не существует, или Вы не его владелец. Если Вы считаете, что это "
                    "ошибка, обратитесь к поддержку",
            errors=["item_not_exists"],
            code=status.HTTP_400_BAD_REQUEST
        )

    if Orders.objects.filter(item=item, is_cancelled=False).exists():
        return error_response(
            heading="Предмет уже заказан",
            message="К сожалению, Вы не можете повторно разместить заказ на вывод предмета, который уже заказан",
            errors=["item_already_ordered"],
            code=status.HTTP_400_BAD_REQUEST
        )
        
    # Create a payment model instance
    payment = Payment.objects.create(
        item=item.item,
        amount=item.item.price,
        owner=request.user,
        currency='RUB'
    )

    return place_order(
        item, genshin_uid, payment, request.data.get("is_test_instance", False)
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_order(request):
    order_id = request.data["id"]

    # Получаем ордер, принадлежащий пользователю
    order = Orders.objects.filter(id=order_id, item__owner=request.user, is_cancelled=False).first()
    if not order:
        return error_response(
            heading="Заказ не существует",
            message="К сожалению, этот заказ не существует. Если Вы считаете, что это "
                    "ошибка, обратитесь к поддержку",
            errors=["order_not_exists"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Если ордер уже на выводе, его нельзя отменить
    if order.step != "processing":
        return error_response(
            heading="Предмет выводится",
            message="К сожалению, этот предмет уже выводится, этот процесс нельзя остановить. Если Вы считаете, что"
                    " это ошибка, обратитесь к поддержку",
            errors=["item_being_withdrawn"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Отменяем ордер
    order.is_cancelled = True
    order.save()

    order.item.is_ordered = False
    order.item.save()

    return success_response(
        heading="Заказ отменен",
        message=f"Вы успешно отменили заказ на \"{order.item.item.name}\"",
        data={},
        code=status.HTTP_200_OK
    )
