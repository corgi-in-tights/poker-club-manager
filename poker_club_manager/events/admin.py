from django.contrib import admin

from .models import PokerEvent, PokerEventAttendee, PokerEventRSVP

admin.site.register(PokerEvent)
admin.site.register(PokerEventAttendee)
admin.site.register(PokerEventRSVP)
