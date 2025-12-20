from django.http import HttpRequest
from django.shortcuts import render

from .models import BlindsTemplate


def timer(request: HttpRequest):
    blinds = BlindsTemplate.objects \
        .global_or_owned(user_id=request.user.id).order_by("updated_at")
    return render(request, "blinds/timer.html", {"blinds": blinds})
