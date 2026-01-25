import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

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

    # Copy the largest index in the context of the same requested level type
    # essentially, PLAY levels skip BREAK levels for quick templating
    # though we still need the actual max index to preserve ordering
    max_index = 0
    max_index_of_same_type = 0
    data = request.GET.dict().copy()
    for key, val in list(data.items()):
        if key.startswith("levels-") and key.endswith("-type"):
            max_index = max(max_index, int(key.split("-")[1]))
            if val == requested_level_type:
                max_index_of_same_type = max(
                    max_index_of_same_type,
                    int(key.split("-")[1]),
                )

    quick_template_index = max_index_of_same_type
    new_index = max_index + 1
    context = {
        "index": new_index,
        "type": requested_level_type,
    }

    prev_level_type = request.GET.get(f"levels-{quick_template_index}-type", "play")
    if requested_level_type == "play":
        if prev_level_type == "play":
            prev_small = int(request.GET.get(f"levels-{quick_template_index}-small", 1))
            prev_big = int(request.GET.get(f"levels-{quick_template_index}-big", 2))
            context["small"] = prev_small * 2
            context["big"] = prev_big * 2
        else:
            context["small"] = 1
            context["big"] = 2

    context["duration"] = int(
        request.GET.get(f"levels-{quick_template_index}-duration", "15"),
    )

    return render(request, "timers/partials/level_field.html", context=context)


def control_timer(request: HttpRequest, timer_id: int):
    timer = get_object_or_404(BlindsTimer, id=timer_id)

    if not request.user.has_perm("events.manage_event"):
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "next" and timer.can_increment_level:
            timer.set_current_level_index(timer.current_level_index + 1)
        elif action == "previous" and timer.can_decrement_level:
            timer.set_current_level_index(timer.current_level_index - 1)
        elif action == "pause" and timer.is_running:
            timer.pause()
        elif action == "resume" and timer.is_paused:
            timer.resume()

    return render(request, "timers/detail.html#timer-controls", {"timer": timer})
