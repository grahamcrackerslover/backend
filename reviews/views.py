from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated

from misc.responses import success_response, error_response
from .models import Review
from .serializers import ReviewSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request):
    # Юзер всегда может оставить отзыв, но если что, модерации надо
    # сначала его проверить, чтобы он отобразился
    data = request.data
    serializer = ReviewSerializer(data=data)

    if serializer.is_valid():
        # Проверить, оставлял ли юзер уже отзыв
        if Review.objects.filter(author=request.user).exists():
            return error_response(
                heading="Отзыв уже оставлен",
                message=f"Кажется, Вы уже оставляли отзыв. Если Вы считаете, что это ошибка, обратитесь в поддержку",
                errors=["review_already_left"],
                code=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(author=request.user)
        return success_response(
            heading="Отзыв оставлен",
            message=f"Спасибо за отзыв! Мы ценим любую похвалу и критику",
            data={"review": serializer.data},
            code=status.HTTP_201_CREATED
        )
    else:
        return error_response(
            heading="Ошибка валидации",
            message=f"Кажется, у Вас не получилось оставить отзыв. Пожалуйста, проверьте, что Вы заполнили текст"
                    f" отзыва и указали оценку. Если ошибка продолжит появляться, обратитесь в поддержку",
            errors=["invalid_review"],
            code=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_review(request):
    review = Review.objects.filter(author=request.user)
    return success_response(
        heading="",
        message="",
        data={
            "review": ReviewSerializer(review).data
        }
    )

@api_view(['GET'])
def list_reviews(request):
    # Запрос будет отправляться в формате /api/reviews/?page=x
    page_number = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page_number - 1) * page_size
    end = start + page_size

    queryset = Review.objects.order_by('-created_at')[start:end]

    # Проверяем есть ли отзывы (надо будет заменить на какой-то код, чтобы
    # фронтенд понимал, есть ли еще отзывы и убирал кнопку
    if not queryset:
        return error_response(
            heading="Отзывы кончились",
            message=f"Вы дочитали до конца отзывов, их не осталось. Вопрос - зачем?",
            errors=["invalid_review"],
            # code=status.HTTP_204_NO_CONTENT
        )

    serializer = ReviewSerializer(queryset, many=True)

    return success_response(
        heading="",
        message="",
        data={"reviews": serializer.data, "page": page_number},
        code=status.HTTP_200_OK
    )


@api_view(['GET'])
def reviews_stats(request):
    # Get the count of positive and negative reviews
    positive_reviews = Review.objects.filter(is_positive=True).count()
    negative_reviews = Review.objects.filter(is_positive=False).count()

    return success_response(
        heading="",
        message="",
        data={
            "positive_reviews": positive_reviews,
            "negative_reviews": negative_reviews
        }
    )