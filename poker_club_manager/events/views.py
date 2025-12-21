import logging
from types import SimpleNamespace

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
    default_filters = SimpleNamespace(
        {
            "order": "relevance",
            "events_per_page": 10,
            "include_finished": "0",
        },
    )

    search_query = request.GET.get("q", "").strip()
    order = request.GET.get("s", default_filters.order)
    include_finished = request.GET.get(
        "include_finished",
        default_filters.include_finished,
    )

    events = (
        EventBrowseFilter(
            search_query=search_query,
            order=order,
            include_finished=include_finished == "1",
        )
        .apply()
        .annotate_rsvp(request.user)
        .annotate_check_in(request.user)
    )

    events_per_page = parse_int(
        request.GET.get("v"),
        default=default_filters.events_per_page,
        min_value=5,
        max_value=50,
    )

    paginator = Paginator(events, events_per_page)
    logger.info(
        "Paginating events: %d per page, %d total pages",
        events_per_page,
        paginator.num_pages,
    )

    page = parse_int(
        request.GET.get("p"),
        default=1,
        min_value=1,
        max_value=paginator.num_pages,
    )
    page_events = paginator.get_page(page)

    context = {"events": page_events, "page": page, "max_page": paginator.num_pages}

    if request.headers.get("HX-Request") == "true":
        return render(request, "events/partials/event_list.html", context=context)

    return render(
        request,
        "events/browse_events.html",
        context={
            **context,
            "filters": SimpleNamespace(
                {
                    "order": order,
                    "events_per_page": events_per_page,
                    "include_finished": include_finished,
                },
            ),
            "search_query": search_query,
            "default_filters": default_filters,
        },
    )


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
        participant = event.add_user_participant(request.user)
        return render(
            request,
            "events/check_in_success.html",
            {"event": event, "participant": participant, "is_guest": False},
        )

    if request.method == "POST":
        form = GuestCheckInForm(request.POST)
        logger.info("Guest check-in for event %s with data %s", event.id, request.POST)
        if form.is_valid():
            logger.info("Guest check-in form valid for event %s", event.id)
            guest = form.save(commit=False)
            participant = event.add_guest_participant(guest.name, guest.email)
            return render(
                request,
                "events/check_in_success.html",
                {"event": event, "participant": participant, "is_guest": True},
            )

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
