from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from poker_club_manager.common.utils.params import parse_int

from .filters import EventBrowseFilter
from .models import Event


def browse_events(request: HttpRequest):
    sort_order = request.GET.get("order", "relevance")
    events = EventBrowseFilter(order=sort_order).apply()

    page = parse_int(request.GET.get("page"), default=1, min_value=1)
    events_per_page = parse_int(
        request.GET.get("events_per_page"), default=20, min_value=5, max_value=50,
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
    active_events = Event.objects.active()
    if not active_events.exists():
        msg = _("There is no active event")
        raise Http404(msg)
    return check_in(request, active_events.first().id)


def check_in(request: HttpRequest, event: int | Event):
    if not isinstance(event, Event):
        try:
            event = Event.objects.get(id=event)
        except Event.DoesNotExist:
            msg = _("The requested event does not exist.")
            raise Http404(msg) from None

    return render(request, "events/check_in.html", {"event": event})

