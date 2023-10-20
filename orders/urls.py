from django.urls import path

from . import views


urlpatterns = [
    path("new/", views.create_order, name="orders-create-order"),  # /api/orders/new/
    path(
        "cancel/", views.cancel_order, name="orders-cancel-order"
    ),  # /api/orders/cancel/
]
