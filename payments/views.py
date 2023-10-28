import math

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from cases.models import Item
from cases.serializers import ItemSerializer
from history.models import HistoryItem as HItem
from misc.responses import success_response, error_response
from orders.views import place_order
from payments.models import BonusCode, PromoCode


def activate_bonus(user, bonus_code):
    if bonus_code and bonus_code.apply(user):
        return success_response(
            heading="Бонус код активирован!",
            message=f"Вы получили {bonus_code.amount} моры!" if bonus_code.promo_type == "money"
                    else f"Вы получили предмет(ы) в инвентарь!",
            data={},
            code=status.HTTP_200_OK
        )

    return error_response(
        heading="Несуществующий бонус код",
        message="Кажется, указаный бонус код не существует. Если Вы считаете, что это ошибка, обратитесь в поддержку",
        errors=["invalid_bonus_code"],
        code=status.HTTP_400_BAD_REQUEST
    )


# class ShopItemViewSet(ModelViewSet):
#     serializer_class = ItemSerializer
#
#     def get_queryset(self):
#         return Item.objects.filter(for_sale=True)


@api_view(["GET"])
def list_all_items(request):
    items = Item.objects.filter(for_sale=True)
    serialized = ItemSerializer(items, many=True)

    return success_response(
        heading="",
        message="",
        data={
            "items": serialized.data
        }
    )


@api_view(["GET"])
def item_details(request, id):
    try:
        return success_response(
            heading="",
            message="",
            data={
                "items": ItemSerializer(Item.objects.get(id=id)).data
            }
        )
    except Item.DoesNotExist:
        return error_response(
            heading="Предмета не существует...",
            message="Запрашиваемый предмет не существует. Если вы считаете, что это ошибка, обратитесь в поддержку.",
            errors=["item_not_exist"]
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_promo(request, code):
    now = timezone.now()
    exists = False
    # Вызывается /api/payments/verify/?code=xxx
    # Если есть и срабатывает, то возвращает True и есть два варианта
    # Если это бонус-код, он сразу активируется, если промо-код, возвращает
    # мультиплаер. Надо как-то сохранить в фронте, чтобы он применялся
    # при пополнении баланса, а не брался именно из формы (короче чтобы
    # брался тот, который уже подтвержден)
    if code:
        promo = PromoCode.objects.filter(
            Q(uses=-1) | Q(uses__gt=0),
            code=code,
            start_date__lte=now,
            end_date__gte=now,
        ).first()
        bonus = BonusCode.objects.filter(
            Q(uses=-1) | Q(uses__gt=0),
            code=code,
            start_date__lte=now,
            end_date__gte=now,
        ).first()

    if promo:
        return success_response(
            heading="",
            message="",
            data={
                "multiplier": promo.percentage
            },
            code=status.HTTP_200_OK
        )

    elif bonus:
        return activate_bonus(request.user, bonus)

    return error_response(
        heading="",
        message="",
        errors=["invalid_promo_or_bonus_code"],
        code=status.HTTP_400_BAD_REQUEST
    )


def plural_mora(n):
    mora = ['монету', 'монеты', 'монет']

    if n % 10 == 1 and n % 100 != 11:
        return mora[0]
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return mora[1]
    else:
        return mora[2]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_balance(request):
    amount = request.data.get("amount")
    if not amount:
        return error_response(
            heading="Сумма не указана",
            message="Кажется, Вы не указали на сколько хотите пополнить баланс",
            errors=["amount_not_specified"],
            code=status.HTTP_400_BAD_REQUEST
        )

    amount = float(amount)
    code = request.data.get("code")
    bonus_amount = 0
    if code:
        promo = PromoCode.objects.filter(code=code).first()
        if promo and promo.apply(amount):
            bonus_amount = promo.apply(amount)
            # Потенциальная ошибка: если пользователь создаст заявку, но не оплатит ее,
            # у промика все равно спишется одно использование. Исправить можно будет
            # когда подключим платежку
        # else:
            # Тк код берется из переменной, в которую он вносится после вызова verify_promo,
            # то эта строчка не только бесполезная, она еще и может сломать что-нибудь,
            # поэтому я ее закомментирую

            # return Response({"error": "Invalid or expired promo code"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO: Подключить платежку

    user = request.user
    user.balance += amount + bonus_amount
    if user.referrer:
        user.referrer.balance += math.ceil(amount / 10)
        user.referrer.save()
    user.save()

    # TODO: добавить мешок моры (или печатей) в инвентарь реферерам

    return success_response(
        heading="Баланс успешно пополнен",
        message=f"Вы внесли {amount + bonus_amount} {plural_mora(amount + bonus_amount)} на свой баланс!"
                f" Успешной игры!",
        data={},
        code=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def shop_buy(request):
    item_id = request.data.get("id")
    genshin_uid = request.data.get("genshin_uid")
    if not item_id:
        return error_response(
            heading="Не указан предмет",
            message="Кажется, произошла ошибка. Обратитесь в поддержку, если это будет продолжаться",
            errors=["item_id_not_specified"],
            code=status.HTTP_400_BAD_REQUEST
        )

    if not genshin_uid:
        return error_response(
            heading="Не указан UID",
            message="Кажется, произошла ошибка. Обратитесь в поддержку, если это будет продолжаться",
            errors=["uid_not_specified"],
            code=status.HTTP_400_BAD_REQUEST
        )

    item = Item.objects.filter(id=item_id).first()
    if not item:
        return error_response(
            heading="Предмет не существует",
            message="Кажется, Вы пытаетесь купить несуществующий предмет. Если Вы считаете, что это ошибка,"
                    " обратитесь в поддержку",
            errors=["shop_item_not_exists"],
            code=status.HTTP_404_NOT_FOUND
        )

    new_hitem = HItem.objects.create(
        item=item,
        owner=request.user if request.user.is_authenticated else None,
        is_ordered=True,
        from_shop=True,
    )

    if request.user.is_authenticated:
        request.user.balance += item.cashback
        request.user.save()

    return place_order(new_hitem, genshin_uid, False)
