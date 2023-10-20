from django.contrib import admin
from .models import Item, Case, CaseItem


class CaseItemInline(admin.TabularInline):
    model = CaseItem
    extra = 1


class CaseAdmin(admin.ModelAdmin):
    inlines = [CaseItemInline]


admin.site.register(Case, CaseAdmin)
admin.site.register(Item)
