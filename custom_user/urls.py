from django.urls import path

from . import views


urlpatterns = [
    path("auth/telegram_login/", views.telegram_auth, name="custom-user-telegram-auth"),  # /api/user/auth/telegram_login
    path("auth/vk_login/", views.vk_auth, name="custom-user-vk-auth"),  # /api/user/auth/vk_login
    path("details/<int:id>", views.details_by_id, name="custom-user-details-by-id"),  # /api/user/details/1
    path("details/", views.details, name="custom-user-details"),  # /api/user/details
    path("inventory/<int:id>", views.inventory_by_id, name="custom-user-inventory-by-id"),  # /api/user/inventory/1
    path("inventory/", views.inventory, name="custom-user-inventory"),  # /api/user/inventory
    path("stats/<int:id>", views.stats_by_id, name="custom-user-stats-by-id"),  # /api/user/stats
    path("stats/", views.stats, name="custom-user-stats"),  # /api/user/stats
]
