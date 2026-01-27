import logging

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from poker_club_manager.common.utils.params import parse_int
from poker_club_manager.events.filters import EventListFilter
from poker_club_manager.events.forms import EventForm, GuestCheckInForm
from poker_club_manager.events.models import Event

logger = logging.getLogger(__name__)


def list_events(request):
    search_query = request.GET.get("q", "").strip()
    order = request.GET.get("s", "relevance")
    include_finished = request.GET.get("include_finished") == "1"

    events_per_page = parse_int(
        request.GET.get("v"),
        default=10,
        minv=5,
        maxv=50,
    )
    page_number = parse_int(request.GET.get("p"), default=1, minv=1)

    events = EventListFilter(
        search_query=search_query,
        order=order,
        include_finished=include_finished,
        user_id=request.user,
    ).apply()
    paginator = Paginator(events, events_per_page)
    page_events = paginator.get_page(page_number)

    context = {
        "events": page_events,
        "page": page_events.number,
        "max_page": paginator.num_pages,
        "filters": {
            "order": order,
            "events_per_page": events_per_page,
            "include_finished": "1" if include_finished else "0",
            "search_query": search_query,
        },
    }

    template = "events/list.html"
    if request.htmx:
        return render(request, f"{template}#event-list", context)

    return render(request, template, context)


class EventDetailView(DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"
    pk_url_kwarg = "event_id"

    def get_queryset(self):
        user = self.request.user
        return (
            Event.objects.annotate_rsvp_count()
            .annotate_check_in(user)
            .annotate_rsvp(user)
        )


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
            "events/check_in.html",
            {
                "event": event,
                "participant": participant,
                "is_guest": False,
                "is_checked_in": True,
            },
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
                "events/check_in.html",
                {
                    "event": event,
                    "participant": participant,
                    "is_guest": True,
                    "is_checked_in": True,
                },
            )

    is_checked_in = (
        event.is_user_participant(request.user)
        if request.user.is_authenticated
        else False
    )

    return render(
        request,
        "events/check_in.html",
        {
            "event": event,
            "guest_form": GuestCheckInForm(),
            "is_checked_in": is_checked_in,
        },
    )


def create_event(request: HttpRequest):
    if not request.user.has_perm("events.add_event"):
        raise PermissionDenied

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return redirect("events:detail", event_id=event.id)
    else:
        form = EventForm()

    return render(request, "events/create.html", {"form": form})
