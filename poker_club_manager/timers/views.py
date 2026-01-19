import json
import logging
import time

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BlindsTimerForm
from .models import BlindsTimer, BlindsTimerLevel

logger = logging.getLogger(__name__)


def active_timers(request: HttpRequest):
    timers = BlindsTimer.objects.active().order_by("created_at")
    return render(request, "timers/active.html", {"timers": timers})


def detail_timer(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer, id=timer_id)
    return render(request, "timers/detail.html", {"timer": timer})


def create_timer(request: HttpRequest):
    if request.method == "POST":
        form = BlindsTimerForm(request.POST)
        if not form.is_valid():
            return render(request, "timers/create.html", {"form": form})

        timer = form.save()

        BlindsTimerLevel.objects.bulk_create(
            [
                BlindsTimerLevel(
                    timer=timer,
                    level_index=i + 1,
                    **lvl,
                )
                for i, lvl in enumerate(form.levels_data)
            ],
        )

        return redirect("timers:detail", timer.id)

    form = BlindsTimerForm()
    return render(request, "timers/create.html", {"form": form})


@require_POST
def timer_control(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer, id=timer_id)

    if not request.user.has_perm("events.manage_event"):
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "next":
            if timer.can_increment_level:
                timer.update_level(timer.current_level_index + 1)
        elif action == "previous":
            if timer.can_decrement_level:
                timer.update_level(timer.current_level_index - 1)
        elif action == "pause":
            timer.pause()
        elif action == "resume":
            timer.resume()

    return render(request, "timers/detail.html#timer_controls", {"timer": timer})
