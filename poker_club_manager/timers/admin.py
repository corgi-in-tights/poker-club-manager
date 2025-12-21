from django.contrib import admin

from .models import BlindsLevel, BlindsTemplate, BlindsTimer

admin.site.register(BlindsTemplate)
admin.site.register(BlindsLevel)
admin.site.register(BlindsTimer)
