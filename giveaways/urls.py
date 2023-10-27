from django.urls import path

from . import views


urlpatterns = [
    path(
        "detail/<int:pk>/", views.giveaway_detail, name="giveaways-giveaway-detail"
    ),  # /api/giveaway/detail/1/
    path(
        "detail/", views.giveaway_detail, name="giveaways-giveaway-detail"
    ),  # /api/giveaway/detail/
    path(
        "participate/", views.participate, name="giveaways-participate"
    ),  # /api/giveaway/participate/
]
