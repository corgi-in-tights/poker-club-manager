from django.contrib import admin

from .models import BlindsTimer, BlindsTimerLevel

admin.site.register(BlindsTimer)
admin.site.register(BlindsTimerLevel)
