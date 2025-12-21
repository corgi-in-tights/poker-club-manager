import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel

User = get_user_model()

MINIMUM_EVENT_ATTENDEES_FOR_RANKING = 5
MAXIMUM_DAYS_FOR_EVENT_RSVP = 14

logger = logging.getLogger(__name__)


class EventQuerySet(models.QuerySet):
    def search(self, query: str):
        logger.info("Searching events with query: %s", query)
        if not query:
            return self

        return self.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
        )

    def finished(self):
        today = timezone.now()
        return self.filter(
            Q(end_date__lt=today) | Q(end_date__isnull=True, start_date__lt=today),
        )

    def unfinished(self):
        today = timezone.now()
        return self.filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today),
        )

    def active(self):
        today = timezone.now()
        return self.filter(start_date__lte=today).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True),
        )

    def by_popularity(self):
        return self.annotate(
            rsvp_count=models.Count("rsvps"),
        ).order_by("-rsvp_count", "start_date")

    def by_start_date(self):
        return self.order_by("start_date")

    def annotate_rsvp(self, user):
        if not user.is_authenticated:
            return self

        return self.annotate(
            is_rsvped=Exists(
                EventRSVP.objects.filter(
                    event=OuterRef("pk"),
                    user=user,
                ),
            ),
        )

    def annotate_check_in(self, user):
        if not user.is_authenticated:
            return self

        return self.annotate(
            is_checked_in=Exists(
                Participant.objects.filter(
                    event=OuterRef("pk"),
                    user=user,
                ),
            ),
        )


class Event(AbstractTimestampedModel):
    objects = EventQuerySet.as_manager()

    season = models.ForeignKey(
        "common.Season",
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Season"),
        null=True,
        blank=True,
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.CharField(_("Description"), blank=True, max_length=1024)

    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"), blank=True, null=True)
    location = models.CharField(_("Location"), blank=True, max_length=255)

    class Meta:
        permissions = [
            ("manage_event", "Can manage event"),
        ]

    def __str__(self):
        return self.title or f"Event {self.id}"

    @property
    def is_active(self) -> bool:
        return self.start_date <= timezone.now() <= self.end_date

    @property
    def is_finished(self) -> bool:
        return timezone.now() > self.end_date

    @property
    def rsvp_start_date(self) -> timezone.datetime:
        return self.start_date - timezone.timedelta(
            days=MAXIMUM_DAYS_FOR_EVENT_RSVP,
        )

    @property
    def is_rsvp_open(self) -> bool:
        # Can only RSVP upto N days before of the event
        now = timezone.now()
        return (
            not self.is_active and not self.is_finished and now >= self.rsvp_start_date
        )

    def rsvp_user(self, user: User, status: str) -> "EventRSVP":
        rsvp, created = EventRSVP.objects.get_or_create(
            user=user,
            event=self,
            defaults={"status": status},
        )
        if created:  # Already RSVPed
            return False

        rsvp.save()
        return rsvp

    def add_user_participant(self, user: User) -> "Participant":
        p, created = Participant.objects.get_or_create(
            event=self,
            user=user,
        )
        if not created:  # Already checked in
            return False

        if self.season is not None:
            if not self.season.user_is_member(user):
                self.season.create_user_membership(user)

        p.save()
        return p

    def add_guest_participant(self, guest_name: str, guest_email: str) -> "Participant":
        p, created = GuestParticipant.objects.get_or_create(
            event=self,
            guest_name=guest_name,
            guest_email=guest_email,
        )
        if not created:  # Already checked in
            return False
        p.save()
        return p

    def user_is_rsvped(self, user: User) -> bool:
        return EventRSVP.objects.filter(user=user, event=self).exists()

    def user_is_participant(self, user: User) -> bool:
        return Participant.objects.filter(user=user, event=self).exists()


class Participant(AbstractTimestampedModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name=_("Event"),
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="participations",
        verbose_name=_("User"),
    )
    final_position = models.PositiveIntegerField(
        _("Final Position"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Participant {self.id} {self.user.username} for Event {self.event.id}"


class GuestParticipant(AbstractTimestampedModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="guests",
        verbose_name=_("Event"),
    )
    name = models.CharField(
        _("Guest Name"),
        max_length=100,
    )
    email = models.EmailField(
        _("Guest Email"),
        blank=True,
    )
    final_position = models.PositiveIntegerField(
        _("Final Position"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Guest Participant {self.id} {self.name} for Event {self.event.id}"


class EventRSVP(AbstractTimestampedModel):
    GOING = "going"
    LATE = "late"
    MAYBE = "maybe"

    STATUS_CHOICES = [
        (GOING, _("Going")),
        (LATE, _("Late")),
        (MAYBE, _("Maybe")),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="rsvps",
    )
    user = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="rsvps",
    )
    # OR
    guest_name = models.CharField(
        max_length=100,
        blank=True,
    )
    guest_email = models.EmailField(
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=GOING,
    )

    class Meta:
        constraints = [
            # Must be either a user OR a guest
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, guest_name="")
                    | models.Q(user__isnull=True, guest_name__gt="")
                ),
                name="rsvp_user_or_guest",
            ),
            # One RSVP per user per event
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=models.Q(user__isnull=False),
                name="unique_user_rsvp",
            ),
            # One RSVP per guest per event (email preferred)
            models.UniqueConstraint(
                fields=["guest_email", "event"],
                condition=models.Q(guest_email__gt=""),
                name="unique_guest_rsvp",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username if self.user else self.guest_name} -"
            f"{self.event.title} ({self.status})"
        )

    @property
    def is_guest(self) -> bool:
        return self.user is None
