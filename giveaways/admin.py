from django.contrib import admin
from django import forms

from custom_user.models import CustomUser
from .models import Giveaway, Item, GiveawayPermissionRule, GiveawayItem, LotteryTicket


def stop_giveaway_and_choose_winners(modeladmin, request, queryset):
    for giveaway in queryset:
        giveaway.choose_winners()


stop_giveaway_and_choose_winners.short_description = (
    "Stop selected giveaways and choose winners"
)


class GiveawayPermissionRuleInline(admin.TabularInline):
    model = Giveaway.permission_rules.through
    extra = 1


class ItemInline(admin.TabularInline):
    model = GiveawayItem
    extra = 1


class GiveawayAdminForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("Participants", is_stacked=False),
        required=False,
    )

    class Meta:
        model = Giveaway
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["participants"].initial = self.instance.participants.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            instance.participants.set(self.cleaned_data["participants"])
            self.save_m2m()
        return instance


class GiveawayAdmin(admin.ModelAdmin):
    # list_display = ('title', 'start_time', 'end_time', 'is_active')
    inlines = [GiveawayPermissionRuleInline, ItemInline]
    # exclude = ('participants', 'winners', 'items')
    actions = [stop_giveaway_and_choose_winners]
    form = GiveawayAdminForm


admin.site.register(Giveaway, GiveawayAdmin)
# admin.site.register(GiveawayWinner)
admin.site.register(GiveawayPermissionRule)
admin.site.register(GiveawayItem)
admin.site.register(LotteryTicket)
