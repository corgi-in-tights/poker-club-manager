from django.contrib import admin

from .models import PokerEvent, PokerEventAttendee

admin.site.register(PokerEvent)
admin.site.register(PokerEventAttendee)
