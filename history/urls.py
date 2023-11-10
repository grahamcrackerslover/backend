from django.urls import path

from . import views


urlpatterns = [
    path("live/", views.live, name="history-live"),  # /api/history/live/
    path(
        "personal/", views.user_history, name="history-personal"
    ),  # /api/history/personal/
    path("sell/", views.sell_items, name="history-sell-item"),  # /api/history/sell/
]
