from django.urls import path

from . import views


urlpatterns = [
    path('balance/', views.add_balance, name='payments-add-balance'),
    path('verify/<str:code>/', views.verify_promo, name='payments-verify-promo'), 
    path('buy/', views.shop_buy, name='payments-shop-buy'),
]