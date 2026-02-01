import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_POST

from poker_club_manager.events.models import Event

logger = logging.getLogger(__name__)
User = get_user_model()


def manage_event(request: HttpRequest, event_id: int):
    event = get_object_or_404(
        Event.objects.annotate_rsvp_count(),
        pk=event_id,
    )
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied

    context = {
        "event": event,
        "participants": event.participants.order_by("user__name"),
        "guests": event.guests.order_by("name"),
        "rsvps": event.rsvps.unarrived().order_by("user__name"),
    }
    return render(request, "events/manage.html", context=context)


@require_POST
def add_participant(request: HttpRequest, event_id: int):
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied
    if not event.is_active:
        msg = "Event is not active"
        return HttpResponseBadRequest(msg)

    if "user_id" not in request.POST:
        msg = "user_id is required"
        return HttpResponseBadRequest(msg)

    user = get_object_or_404(User, pk=request.POST.get("user_id"))
    event.add_user_participant(user)

    return render(
        request,
        "events/manage.html#participant-list",
        {"event": event, "participants": event.participants.order_by("user__name")},
    )


@require_http_methods(["DELETE"])
def eliminate_participant(request: HttpRequest, event_id: int, participant_id: int):
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied
    if not event.is_active:
        msg = "Event is not active"
        return HttpResponseBadRequest(msg)

    event.remove_user_participant(participant_id=participant_id)

    return render(
        request,
        "events/manage.html#participant-list",
        {"event": event, "participants": event.participants.order_by("user__name")},
    )


@require_POST
def add_guest(request: HttpRequest, event_id: int):
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied

    if "name" not in request.POST or "email" not in request.POST:
        msg = "name and email are required"
        return HttpResponseBadRequest(msg)

    name = request.POST.get("name")
    email = request.POST.get("email")
    event.add_guest_participant(name, email)

    return render(
        request,
        "events/manage.html#guest-list",
        {"event": event, "guests": event.guests.order_by("name")},
    )


@require_http_methods(["DELETE"])
def remove_guest(request: HttpRequest, event_id: int, guest_id: int):
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied

    event.remove_guest_participant(guest_id=guest_id)

    return render(
        request,
        "events/manage.html#guest-list",
        {"event": event, "guests": event.guests.order_by("name")},
    )


@require_http_methods(["GET"])
def manage_search_users(request: HttpRequest, event_id: int):
    event = get_object_or_404(Event, pk=event_id)
    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied

    query = request.GET.get("participant_identifier", "")
    results = []
    if query:
        results = User.objects.filter_by_name(query)[:3]

    return render(
        request,
        "events/partials/manage_search_users.html",
        {"event": event, "results": results},
    )


@require_POST
def start_end_event(request: HttpRequest, event_id: int):
    if not request.user.has_perm("events.manage_event"):
        raise PermissionDenied

    event = get_object_or_404(Event.objects.all(), pk=event_id)
    # If not finished, start or end the event
    if not event.is_finished:
        if event.is_active:
            event.set_finished()
        else:
            event.set_active()

    return render(
        request,
        "events/partials/event_state_control.html",
        {"event": event},
    )


@require_POST
def open_close_rsvp(request: HttpRequest, event_id: int):
    if not request.user.has_perm("events.manage_event"):
        raise PermissionDenied

    event = get_object_or_404(Event.objects.annotate_rsvp(request.user), pk=event_id)

    return render(
        request,
        "events/partials/event_state_control.html",
        {"event": event},
    )
