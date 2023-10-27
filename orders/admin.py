from django.contrib import admin

from orders.models import Orders, Wallet

admin.site.register(Orders)
admin.site.register(Wallet)
