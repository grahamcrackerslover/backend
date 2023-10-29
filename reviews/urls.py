from django.urls import path
from . import views

urlpatterns = [
    path(
        "create/", views.create_review, name="reviews-create-review"
    ),  # /api/reviews/create/
    path("", views.list_reviews, name="reviews-list-reviews"),  # /api/reviews/?page=x
    path("user/", views.users_review, name="reviews-users-review")
]
