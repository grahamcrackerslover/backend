from django.urls import path

from . import views

urlpatterns = [
    path("details/<int:pk>/", views.get_case_details, name="cases-get-case-details"),  # api/case/details/1
    path("open/<int:pk>/", views.open_case, name="cases-open-case"),  # /api/case/open/1/
    path("all/", views.get_all_cases, name="cases-get-all-cases"),  # /api/case/all
    path('similar/', views.get_similar_priced_cases, name="cases-get-similar=priced-cases"),
]
