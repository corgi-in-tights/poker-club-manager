from django.contrib import admin

from .models import Event, EventRSVP, Participant

admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(EventRSVP)
