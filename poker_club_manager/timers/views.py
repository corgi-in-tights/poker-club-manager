from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import BlindsTemplate, BlindsTimer


def active_timers(request: HttpRequest):
    timers = BlindsTimer.objects.all().order_by("created_at")
    return render(request, "timers/active.html", {"timers": timers})


def timer_detail(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer, id=timer_id)
    return render(request, "timers/detail.html", {"timer": timer})


def new_timer(request: HttpRequest):
    blinds_templates = BlindsTemplate.objects.global_or_owned(request.user.id).order_by(
        "updated_at",
    )
    return render(request, "timers/new.html", {"blinds_templates": blinds_templates})
