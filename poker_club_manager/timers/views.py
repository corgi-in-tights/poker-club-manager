import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BlindsTimerForm
from .models import BlindsTimer, BlindsTimerLevel

logger = logging.getLogger(__name__)


def active_timers(request: HttpRequest):
    timers = BlindsTimer.objects.active().order_by("created_at")
    return render(request, "timers/active.html", {"timers": timers})


def detail_timer(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer.objects.all(), id=timer_id)
    level = timer.get_current_level()
    hours, minutes, seconds = timer.get_remaining_time()

    return render(
        request,
        "timers/detail.html",
        {
            "timer": timer,
            "level": level,
            "display": {
                "hours": round(hours),
                "minutes": round(minutes),
                "seconds": round(seconds),
            },
        },
    )


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


def level_field_partial(request: HttpRequest):
    requested_level_type = request.GET.get("type", "play")

    prev_index = int(request.GET.get("index"))
    new_index = prev_index + 1
    context = {
        "index": new_index,
        "type": requested_level_type,
    }

    prev_level_type = request.GET.get(f"levels-{prev_index}-type", "play")
    if requested_level_type == "play":
        if prev_level_type == "play":
            prev_small = int(request.GET.get(f"levels-{prev_index}-small", 1))
            prev_big = int(request.GET.get(f"levels-{prev_index}-big", 2))
            context["small"] = prev_small * 2
            context["big"] = prev_big * 2
        else:
            context["small"] = 1
            context["big"] = 2

    context["duration"] = int(request.GET.get(f"levels-{prev_index}-duration", "15"))

    return render(request, "timers/partials/level_field.html", context=context)


@require_POST
def control_timer(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer, id=timer_id)

    if not request.user.has_perm("events.manage_event"):
        raise PermissionDenied

    action = request.POST.get("action")
    if action == "next":
        if timer.can_increment_level:
            timer.set_current_level_index(timer.current_level_index + 1)
    elif action == "previous":
        if timer.can_decrement_level:
            timer.set_current_level_index(timer.current_level_index - 1)
    elif action == "pause":
        timer.pause()
    elif action == "resume":
        timer.resume()
    return render(request, "timers/detail.html#timer_controls", {"timer": timer})
