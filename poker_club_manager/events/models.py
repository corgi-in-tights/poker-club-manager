from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel, SeasonMembership

from .signals import event_completed

User = get_user_model()

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
        # Either ended_at is set or end_date is in the past
        return self.filter(
            Q(ended_at__isnull=False) | Q(end_date__lt=today),
        )

    def unfinished(self):
        today = timezone.now()
        # ended_at must not be set and end_date must be in the future
        return self.filter(
            Q(ended_at__isnull=True, end_date__gt=today),
        )

    def active(self):
        today = timezone.now()
        # ended_at must not be set
        # then, either started_at is set
        # or current date is within start_date and end_date
        return self.filter(Q(ended_at__isnull=True)).filter(
            Q(started_at__isnull=False) | Q(start_date__lte=today, end_date__gte=today),
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

    def annotate_rsvp_count(self):
        return self.annotate(
            going_count=Count("rsvps", filter=Q(rsvps__status=EventRSVP.GOING)),
            late_count=Count("rsvps", filter=Q(rsvps__status=EventRSVP.LATE)),
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
    scoring_strategy = models.CharField(
        max_length=50,
        blank=True,
        default=settings.POINTS_DEFAULT_SCORING_STRATEGY,
    )

    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"))
    rsvp_enabled = models.BooleanField(_("Allow RSVPs"), default=True)
    rsvp_start_date = models.DateTimeField(_("RSVP Start Date"), null=True, blank=True)
    location = models.CharField(_("Location"), blank=True, max_length=255)

    started_at = models.DateTimeField(_("Started At"), blank=True, null=True)
    ended_at = models.DateTimeField(_("Ended At"), blank=True, null=True)

    class Meta:
        permissions = [
            ("manage_event", "Can manage event"),
        ]

    def __str__(self):
        return self.title or f"Event {self.id}"

    def save(self, *args, **kwargs):
        # If RSVP is enabled and no RSVP start date is set, give it a default value
        if self.rsvp_enabled and not self.rsvp_start_date:
            self.rsvp_start_date = self.start_date - timezone.timedelta(
                days=MAXIMUM_DAYS_FOR_EVENT_RSVP,
            )
        return super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.started_at or self.start_date <= timezone.now() <= self.end_date

    @property
    def is_finished(self) -> bool:
        return self.ended_at or timezone.now() > self.end_date

    @property
    def is_rsvp_open(self) -> bool:
        if (
            not self.rsvp_enabled
            or not self.rsvp_start_date
            or self.is_active
            or self.is_finished
        ):
            return False
        now = timezone.now()
        return (
            not self.is_active and not self.is_finished and now >= self.rsvp_start_date
        )

    def rsvp_user(self, user: User, status: str) -> EventRSVP:
        if not self.is_rsvp_open:
            return False

        rsvp, created = EventRSVP.objects.get_or_create(
            user=user,
            event=self,
            defaults={"status": status},
        )
        if not created:  # Already RSVPed
            return False

        rsvp.save()
        return True

    def cancel_rsvp_user(self, user: User) -> bool:
        try:
            rsvp = EventRSVP.objects.get(user=user, event=self)
            rsvp.delete()
        except ObjectDoesNotExist:
            return False
        return True

    def add_user_participant(self, user: User) -> Participant:
        p, created = Participant.objects.get_or_create(
            event=self,
            user=user,
        )
        if not created:  # Already checked in
            return False

        if self.season is not None:
            if not self.season.is_user_member(user):
                self.season.create_user_membership(user)

        # If user RSVP'd
        try:
            rsvp = EventRSVP.objects.get(user=user, event=self)
            rsvp.status = EventRSVP.ARRIVED
            rsvp.arrival_time = timezone.now()
            rsvp.save()
        except ObjectDoesNotExist:
            pass

        p.save()
        return p

    def remove_user_participant(
        self,
        participant_id: int | None = None,
        participant: Participant = None,
        user: User = None,
    ) -> bool:
        try:
            if participant_id is not None:
                participant = Participant.objects.get(id=participant_id, event=self)
            elif user is not None:
                participant = Participant.objects.get(event=self, user=user)
            elif participant is None:
                msg = "Either participant_id or user must be provided."
                raise ValueError(msg)
            participant.delete()
        except ObjectDoesNotExist:
            return False
        return True

    def add_guest_participant(
        self,
        name: str,
        email: str,
    ) -> GuestParticipant:
        p, created = GuestParticipant.objects.get_or_create(
            event=self,
            name=name,
            email=email.lower(),
        )
        if not created:  # Already checked in
            return False
        p.save()
        return p

    def remove_guest_participant(
        self,
        guest_id: int | None = None,
        email: str | None = None,
    ) -> bool:
        try:
            if guest_id is not None:
                guest = GuestParticipant.objects.get(
                    id=guest_id,
                    event=self,
                )
            elif email is not None:
                guest = GuestParticipant.objects.get(
                    event=self,
                    email=email.lower(),
                )
            else:
                msg = "Either guest_id or email must be provided."
                raise ValueError(msg)

            guest.delete()
        except ObjectDoesNotExist:
            return False
        return True

    def is_user_rsvped(self, user: User) -> bool:
        return EventRSVP.objects.filter(user=user, event=self).exists()

    def is_user_participant(self, user: User) -> bool:
        return Participant.objects.filter(user=user, event=self).exists()

    def get_total_participants(self) -> int:
        return self.participants.count() + self.guests.count()

    def set_active(self) -> bool:
        if self.is_active:
            return False
        self.started_at = timezone.now()
        self.save()
        return True

    def set_finished(self) -> bool:
        if not self.is_active:
            return False
        event_completed.send(sender=self.__class__, event=self)
        self.ended_at = timezone.now()
        self.save()
        return True


class ParticipantQuerySet(models.QuerySet):
    def with_membership_for_season(self, season):
        return self.select_related("user").prefetch_related(
            Prefetch(
                "user__memberships",
                queryset=SeasonMembership.objects.filter(season=season),
                to_attr="membership_for_season",
            ),
        )


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
    eliminations = models.PositiveIntegerField(
        _("Eliminations"),
        default=0,
    )

    objects = ParticipantQuerySet.as_manager()

    def __str__(self):
        return f"Participant {self.id} {self.user.username} for Event {self.event.id}"

    @property
    def season_membership(self) -> SeasonMembership | None:
        if self.event.season is None:
            return None
        return self.event.season.get_membership_for_user(self.user)


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


class EventRSVPQueryset(models.QuerySet):
    def arrived(self):
        return self.filter(status=EventRSVP.ARRIVED)

    def unarrived(self):
        return self.filter(~models.Q(status=EventRSVP.ARRIVED))

    def going(self):
        return self.filter(status=EventRSVP.GOING)

    def late(self):
        return self.filter(status=EventRSVP.LATE)

    def maybe(self):
        return self.filter(status=EventRSVP.MAYBE)


class EventRSVP(AbstractTimestampedModel):
    objects = EventRSVPQueryset.as_manager()

    ARRIVED = "arrived"
    GOING = "going"
    LATE = "late"
    MAYBE = "maybe"

    STATUS_CHOICES = [
        (ARRIVED, _("Arrived")),
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

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=GOING,
    )
    arrival_time = models.DateTimeField(
        _("Arrival Time"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Event RSVP")
        verbose_name_plural = _("Event RSVPs")
        constraints = [
            # One RSVP per user per event
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=models.Q(user__isnull=False),
                name="unique_user_rsvp",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

    @property
    def is_guest(self) -> bool:
        return self.user is None
