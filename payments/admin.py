from django.contrib import admin
from .models import BonusCode, Code, PromoCode
from history.models import HistoryItem as HItem
from cases.models import Item


class BonusCodeItemInline(admin.TabularInline):
    model = BonusCode.items.through
    extra = 1


class BonusCodeAdmin(admin.ModelAdmin):
    inlines = [BonusCodeItemInline]
    exclude = ("items",)


# admin.site.register(Code)
admin.site.register(BonusCode, BonusCodeAdmin)
admin.register(PromoCode)
