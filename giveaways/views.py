import math

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from custom_user.models import CustomUser
from misc.responses import success_response, error_response
from .models import Giveaway, LotteryTicket
from .serializers import GiveawaySerializer, GiveawayParticipantSerializer


@api_view(["GET"])
def giveaway_detail(request, pk=None):
    user = request.user
    # Да тут на английском и мне лень переделывать
    if pk is None:
        giveaway = Giveaway.objects.filter(is_active=True).first()
        if giveaway is None:
            return error_response(
                heading="Раздач нет...",
                message="Сейчас на сайте нет запущенных раздач. Но не расстраивайтесь, они скоро появятся!",
                errors=["no_active_giveaway"],
                code=status.HTTP_400_BAD_REQUEST
            )
    else:
        try:
            giveaway = Giveaway.objects.get(pk=pk)
        except Giveaway.DoesNotExist:
            return error_response(
                heading="Раздачи не существует",
                message="Такой раздачи не существует, попробуйте перезагрузить страницу или заново открыть вкладку"
                        " с раздачами",
                errors=["giveaway_does_not_exists"],
                code=status.HTTP_404_NOT_FOUND
            )

    # Check if the user has joined the giveaway
    joined = (
        user.participated_giveaways.filter(id=giveaway.id).exists()
        if type(user) == CustomUser
        else False
    )

    # Serialize the data
    giveaway_serializer = GiveawaySerializer(giveaway)
    giveaway_data = giveaway_serializer.data

    # Add the joined field to the serialized data
    giveaway_data["joined"] = joined

    # Get the participants count
    participants_count = giveaway.participants.count()

    # Add the participants count field to the serialized data
    giveaway_data["participants_count"] = participants_count

    # Get the participants
    participants = giveaway.participants.all()

    # Serialize the participants
    participants_serializer = GiveawayParticipantSerializer(participants, many=True)

    # Add the participants field to the serialized data
    giveaway_data["participants"] = participants_serializer.data

    # Если тип розыгрыша - лотерея, то там можно купить до 5 билетов
    if giveaway.type == "lottery":
        giveaway_data["tickets"] = 0
        if LotteryTicket.objects.filter(user=user, giveaway=giveaway).exists():
            users_tickets = LotteryTicket.objects.get(user=user, giveaway=giveaway)
            giveaway_data["tickets"] = users_tickets.tickets
            giveaway_data["next_ticket_price"] = giveaway.price + math.ceil(
                users_tickets.tickets * giveaway.price * 0.5
            )

    return success_response(
        heading="",
        message="",
        data={"giveaway": giveaway_data},
        code=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def participate(request):
    # Проверяем что розыгрыш существует
    giveaway = Giveaway.objects.filter(is_active=True).first()
    if giveaway is None:
        return error_response(
            heading="Раздач нет...",
            message="Сейчас на сайте нет запущенных раздач. Но не расстраивайтесь, они скоро появятся!",
            errors=["no_active_giveaway"],
            code=status.HTTP_400_BAD_REQUEST
        )
    user = request.user

    # Проверяем что юзер подходит под условия
    if not giveaway.user_meets_permission_rules(user):
        return error_response(
            heading="Не выполнены условия",
            message="Кажется, Вы не выполнили условия, необходимые для участия в раздаче. Если Вы считаете, что это"
                    " ошибка, обратитесь в поддержку",
            errors=["requirements_not_met"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Проверяем что у юзера есть деньги
    if user.balance < giveaway.price:
        return error_response(
            heading="Не хватает моры",
            message="Пополните баланс или накопите побольше моры, чтобы поучаствовать!",
            errors=["insufficient_balance"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Если тип - раздача
    if giveaway.type == "normal":
        # Если юзер еще не участвовал, ему можно
        if user not in giveaway.participants.all():
            giveaway.participants.add(user)
            user.balance -= giveaway.price

            user.save()
            giveaway.save()
            return success_response(
                heading="Вы приняли участие в раздаче!",
                message="Дождитесь конца раздачи чтобы узнать, выиграли Вы или нет. Удачи!",
                data={},
                code=status.HTTP_200_OK
            )
        else:
            return error_response(
                heading="Вы уже участвуете!",
                message="К сожалению, Вы не можете поучаствовать в этой раздаче несколько раз",
                errors=["already_a_participant"],
                code=status.HTTP_400_BAD_REQUEST
            )

    # Если тип - лотерея
    elif giveaway.type == "lottery":
        lottery_tickets = LotteryTicket.objects.filter(user=user, giveaway=giveaway)

        if lottery_tickets.exists():
            lottery_ticket = lottery_tickets.first()
            if lottery_ticket.tickets >= 5:
                return error_response(
                    heading="Достигнут лимит билетов!",
                    message="К сожалению, Вы не можете купить более пяти билетов",
                    errors=["max_tickets"],
                    code=status.HTTP_400_BAD_REQUEST
                )
            next_ticket_price = giveaway.price + math.ceil(
                lottery_ticket.tickets * giveaway.price * 0.5
            )
            lottery_ticket.tickets += 1
        else:
            lottery_ticket = LotteryTicket(user=user, giveaway=giveaway)
            next_ticket_price = giveaway.price

        user.balance -= next_ticket_price
        user.save()
        lottery_ticket.save()

        return success_response(
            heading="Вы приняли участие в лотерее!",
            message="Дождитесь конца лотереи чтобы узнать, выиграли Вы или нет. Удачи!",
            data={},
            code=status.HTTP_200_OK
        )

    else:
        return error_response(
            heading="Неизвестный тип раздачи",
            message="Скорее всего, Вы намеренно делаете запрос к серверу с несуществующим типом раздачи, Кли"
                    " расстроена.. если это не так, обратитесь в поддержку",
            errors=["incorrect_giveaway_type"],
            code=status.HTTP_400_BAD_REQUEST
        )
