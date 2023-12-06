from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views
# from .views import ShopItemViewSet

# router = SimpleRouter()
# router.register(r'items', ShopItemViewSet, basename='payments-items')

urlpatterns = [
    # path('', include(router.urls)),
    path('items/', views.list_all_items, name='payments-list-all-items'),
    path('item/<int:id>/', views.item_details, name='payments-item-details'),
    path('balance/', views.add_balance, name='payments-add-balance'),
    path('verify/<str:code>/', views.verify_promo, name='payments-verify-promo'), 
    path('buy/', views.shop_buy, name='payments-shop-buy'),
    path('uid_details/', views.uid_details, name='payments-uid-details'),
    path('payments/<int:pk>/', views.payment_detail, name='payment-detail'),
]