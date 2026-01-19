from django.contrib import admin

from .models import BlindsSchedule, BlindsScheduleLevel, BlindsTimer, BlindsTimerLevel

admin.site.register(BlindsSchedule)
admin.site.register(BlindsScheduleLevel)
admin.site.register(BlindsTimer)
admin.site.register(BlindsTimerLevel)
