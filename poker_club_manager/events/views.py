import logging
from types import SimpleNamespace

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from poker_club_manager.common.utils.params import parse_int

from .filters import EventListFilter
from .forms import EventForm, GuestCheckInForm
from .models import Event, EventRSVP

logger = logging.getLogger(__name__)


def list_events(request: HttpRequest):
    default_filters = SimpleNamespace(
        {
            "order": "relevance",
            "events_per_page": 10,
            "include_finished": "0",
            "search_query": "",
        },
    )

    search_query = request.GET.get("q", "").strip()
    order = request.GET.get("s", default_filters.order)
    include_finished = request.GET.get(
        "include_finished",
        default_filters.include_finished,
    )

    events = (
        EventListFilter(
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
        return render(request, "events/list.html#event-cards", context=context)

    return render(
        request,
        "events/list.html",
        context={
            **context,
            "filters": SimpleNamespace(
                {
                    "order": order,
                    "events_per_page": events_per_page,
                    "include_finished": include_finished,
                    "search_query": search_query,
                },
            ),
            "default_filters": default_filters,
        },
    )


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


def manage_event(request: HttpRequest, event_id: int):
    event = get_object_or_404(
        Event.objects.annotate_rsvp_count(),
        pk=event_id,
    )

    if not request.user.has_perm("events.manage_event", event):
        raise PermissionDenied

    context = {
        "event": event,
        "participants": event.participants.order_by("user__username"),
        "guests": event.guests.order_by("name"),
        "rsvps": event.rsvps.unarrived().order_by("user__username"),
    }
    return render(request, "events/manage.html", context=context)


@require_http_methods(["GET", "POST"])
def rsvp_button(request: HttpRequest, event_id: int, rsvp_status=EventRSVP.GOING):
    event = get_object_or_404(Event.objects.annotate_rsvp(request.user), pk=event_id)
    rsvped = event.is_rsvped

    if request.method == "POST":
        if not request.user.is_authenticated:
            raise PermissionDenied

        if rsvped:
            event.cancel_rsvp_user(request.user)
            rsvped = False
        else:
            event.rsvp_user(request.user, rsvp_status)
            rsvped = True

    return render(
        request,
        "events/partials/rsvp_button.html",
        {"event": event, "rsvped": rsvped},
    )
