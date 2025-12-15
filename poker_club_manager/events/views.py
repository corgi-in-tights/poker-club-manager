from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import DetailView

from .models import PokerEvent


def browse_events(request: HttpRequest):
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    try:
        events_per_page = max(5, min(50, int(request.GET.get("events_per_page", 20))))
    except ValueError:
        events_per_page = 20

    sort_order = request.GET.get("order", "asc")
    if sort_order not in {"asc", "desc"}:
        sort_order = "asc"

    event_types = request.GET.getlist("event_types", [])
    for i, event_type in enumerate(event_types):
        if event_type not in {"tournament", "special", "other"}:
            del event_types[i]
            break

    events = PokerEvent.objects.unfinished().order_by(
        "start_date" if sort_order == "asc" else "-start_date",
    )
    p = Paginator(events, events_per_page)
    page_events = p.get_page(page)

    return render(request, "events/home.html", {"events": page_events})


class EventDetailView(DetailView):
    model = PokerEvent
    template_name = "events/event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"
