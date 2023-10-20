from django.contrib import admin

# Register your models here.
from .models import HistoryCase, HistoryItem

admin.site.register(HistoryCase)
admin.site.register(HistoryItem)
