from django.contrib import admin

from .models import Season, SeasonMembership

admin.site.register(Season)


@admin.register(SeasonMembership)
class SeasonMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "season")
    ordering = ("-season__name", "user__name")
