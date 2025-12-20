from django.contrib import admin

from .models import BlindsLevel, BlindsTemplate

admin.site.register(BlindsTemplate)
admin.site.register(BlindsLevel)
