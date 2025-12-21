import logging

from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from poker_club_manager.common.utils.params import parse_int

from .filters import EventBrowseFilter
from .forms import GuestCheckInForm
from .models import Event

logger = logging.getLogger(__name__)


def browse_events(request: HttpRequest):
    sort_order = request.GET.get("order", "relevance")
    events = (
        EventBrowseFilter(
            order=sort_order,
            include_finished=request.GET.get("include_finished", "0") == "1",
        )
        .apply()
        .annotate_rsvp(request.user)
        .annotate_check_in(request.user)
    )

    logger.info("These are the events being browsed: %s", events)

    page = parse_int(request.GET.get("page"), default=1, min_value=1)
    events_per_page = parse_int(
        request.GET.get("events_per_page"),
        default=20,
        min_value=5,
        max_value=50,
    )

    p = Paginator(events, events_per_page)
    page_events = p.get_page(page)

    return render(request, "events/browse_events.html", {"events": page_events})


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"


def check_into_first_active(request: HttpRequest):
    event = Event.objects.active().first()
    if event is None:
        raise Http404(_("There is no active event"))
    return redirect("events:check_in", event_id=event.id)


def check_in(request: HttpRequest, event_id: int):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST" and request.user.is_authenticated:
        event.add_user_participant(request.user)
        return render(
            request,
            "events/check_in_success.html",
            {"event": event},
        )

    if request.method == "POST":
        form = GuestCheckInForm(request.POST)
        if form.is_valid():
            guest = form.save(commit=False)
            guest.event = event
            guest.save()
            return redirect("events:check_in", event_id=event.id)
    else:
        form = GuestCheckInForm()

    return render(
        request,
        "events/check_in.html",
        {
            "event": event,
            "guest_form": form,
        },
    )
