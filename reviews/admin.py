from django.contrib import admin
from django import forms
from .models import Review, Reply


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["name", "text"]


class ReplyInline(admin.StackedInline):
    model = Reply
    form = ReplyForm
    extra = 0


class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "is_positive", "text", "author", "created_at", "is_allowed"]
    inlines = [ReplyInline]


admin.site.register(Review, ReviewAdmin)
admin.site.register(Reply)
