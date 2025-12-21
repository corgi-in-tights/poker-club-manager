from django.contrib import admin

from .models import Event, EventRSVP, GuestParticipant, Participant

admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(EventRSVP)
admin.site.register(GuestParticipant)
