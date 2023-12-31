import logging
import random
import string

from django.db import models
from django.db.models import ExpressionWrapper, F
from django.db.models.functions import Abs, Cast
from django.utils import timezone
# Create your views here.
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated

from cases.models import Case, CaseItem
from cases.serializers import ItemSerializer, CaseSerializer
from custom_user.models import CustomUser
from history.models import HistoryCase as HCase
from history.models import HistoryItem as HItem
from misc.responses import success_response, error_response
from logs.models import Log


@api_view(["GET"])
def get_all_cases(request):
    """

    Получает список всех кейсов

    """
    cases = Case.objects.all()
    serialized_cases = CaseSerializer(cases, many=True)

    # Тут экспериментальный вид ответа, я в будущем все под такой
    # хотел подогнать, чтобы фронту легче было читать
    Log.info(
        user=request.user if isinstance(request.user, CustomUser) else None,
        ip=request.META.get('REMOTE_ADDR'),
        request_url=request.path,
        http_method=request.method
    )
    return success_response(
        heading="",
        message="",
        data={
            "cases": serialized_cases.data
        }
    )


@api_view(["GET"])
def get_case_details(request, pk):
    # Другой подход к проверке, существует ли кейс
    # по сути должен меньше нагружать бд
    # case = get_object_or_404(Case, id=pk) <-- так тоже можно,
    # но формат ответа будет другим

    try:
        case = Case.objects.get(id=pk)
    except Case.DoesNotExist:
        Log.warn(
            user=request.user if isinstance(request.user, CustomUser) else None,
            ip=request.META.get('REMOTE_ADDR'),
            request_url=request.path,
            http_method=request.method
        )
        return error_response(
            heading="Не найдено",
            message="Мы не нашли такой кейс...",
            errors=["case_not_found"],
            code=status.HTTP_404_NOT_FOUND
        )

    serialized_data = CaseSerializer(case)
    return success_response(
        heading="",
        message="",
        data={
            "case": serialized_data.data
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def open_case(request, pk):
    # Другой подход к проверке, существует ли кейс
    # по сути должен меньше нагружать бд
    try:
        case = Case.objects.get(id=pk)
    except Case.DoesNotExist:
        return error_response(
            heading="Не найдено",
            message="Мы не нашли такой кейс...",
            errors=["case_not_found"],
            code=status.HTTP_404_NOT_FOUND
        )

    # Если у юзера не хватает денег, вернуть ошибку
    if request.user.balance < case.price:
        return error_response(
            heading="Не хватает моры",
            message="Пополните баланс или накопите побольше моры, чтобы открыть этот кейс!",
            errors=["insufficient_balance"],
            code=status.HTTP_400_BAD_REQUEST
        )

    # Получить предметы, составить 2 списка и выбрать
    # рандомный с шансами
    case_items = CaseItem.objects.filter(case_id=pk)
    items = [case_item.item for case_item in case_items]
    drop_rates = [case_item.drop_rate for case_item in case_items]

    random_item = random.choices(items, weights=drop_rates, k=1)[0]

    # Создаем в "историю" новый предмет и кейс
    new_item = HItem.objects.create(
        item=random_item,
        owner=request.user
    )

    HCase.objects.create(
        case=case,
        item=new_item,
        user=request.user,
        opened_at=timezone.now(),
    )

    serialized_item = ItemSerializer(random_item)
    request.user.balance -= case.price
    request.user.save()

    return success_response(
        heading="",
        message="",
        data={
            "item": serialized_item.data
        }
    )


@api_view(["GET"])
def get_similar_priced_cases(request):
    case_id = request.query_params.get('id')
    number_of_cases = request.query_params.get('n')

    if not number_of_cases.isnumeric() or int(number_of_cases) <= 0:
        return error_response(
            heading="Неверный параметр",
            message="Число кейсов должно быть натуральным",
            errors=["invalid_number_of_cases"],
            code=status.HTTP_400_BAD_REQUEST
        )
    try:
        # Получаем цену для заданного случая
        target_case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return error_response(
            heading="Case Not Found",
            message="A case with the provided ID does not exist.",
            errors=["case_not_found"],
            code=status.HTTP_404_NOT_FOUND
        )

        # Получаем N ближайших по цене случаев, исключая сам случай
    similar_cases = Case.objects.annotate(
        price_diff=ExpressionWrapper(
            Abs(Cast(F('price'), models.IntegerField()) - target_case.price),
            output_field=models.IntegerField())
    ).exclude(id=target_case.id).order_by('price_diff')[:int(number_of_cases)]

    # Формируем данные для ответа
    similar_cases_data = CaseSerializer(similar_cases, many=True).data

    return success_response(
        heading="Similar Priced Cases",
        message="Successfully retrieved cases similar in price.",
        data=similar_cases_data,
        code=status.HTTP_200_OK
    )
