from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel


class PokerEventQuerySet(models.QuerySet):
    def finished(self):
        today = timezone.now().date()
        return self.filter(
            Q(end_date__lt=today) | Q(end_date__isnull=True, start_date__lt=today),
        )

    def unfinished(self):
        today = timezone.now().date()
        return self.filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today),
        )

    def active(self):
        today = timezone.now().date()
        return self.filter(start_date__lte=today).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True),
        )


class PokerEvent(AbstractTimestampedModel):
    objects = PokerEventQuerySet.as_manager()

    title = models.CharField(_("Title"), max_length=255)
    description = models.CharField(_("Description"), blank=True, max_length=1024)

    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"), blank=True, null=True)
    location = models.CharField(_("Location"), blank=True, max_length=255)

    def __str__(self):
        return self.title or f"PokerEvent {self.id}"

    @property
    def is_active(self) -> bool:
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date == today

    @property
    def is_finished(self) -> bool:
        today = timezone.now().date()
        if self.end_date:
            return today > self.end_date
        return today > self.start_date


class PokerEventAttendee(AbstractTimestampedModel):
    event = models.ForeignKey(
        PokerEvent,
        on_delete=models.CASCADE,
        related_name="attendees",
        verbose_name=_("Event"),
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="event_attendances",
        verbose_name=_("User"),
    )
    final_position = models.PositiveIntegerField(_("Rank"), null=True, blank=True)
    points_earned = models.IntegerField(_("Points Earned"), default=0)
    times_eliminated = models.PositiveIntegerField(_("Times Eliminated"), default=0)

    def __str__(self):
        return f"Attendee {self.id} {self.user.username} for Event {self.event.id}"

    @property
    def is_eliminated(self) -> bool:
        return self.times_eliminated > 0
