import logging

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel

logger = logging.getLogger(__name__)


class BlindsScheduleQuerySet(models.QuerySet):
    def global_or_owned(self, user_id):
        if user_id is None:
            return self.filter(is_global=True)
        return self.filter(
            Q(is_global=True) | Q(created_by__isnull=False, created_by=user_id),
        )


class BlindsSchedule(AbstractTimestampedModel):
    name = models.CharField(_("Name"), max_length=255)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="blinds_schedules",
        verbose_name=_("Created By"),
        null=True,
        blank=True,
    )
    is_global = models.BooleanField(_("Is Global"), default=False)

    objects = BlindsScheduleQuerySet.as_manager()

    class Meta:
        verbose_name = _("Blinds Schedule")
        verbose_name_plural = _("Blinds Schedules")

    def __str__(self):
        return self.name


class BlindsTimerQuerySet(models.QuerySet):
    def active(self):
        return self.filter(Q(is_finished=False))


class BlindsTimer(AbstractTimestampedModel):
    name = models.CharField(_("Name"), max_length=255)
    event = models.ForeignKey(
        "events.Event",
        related_name="timers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    start_level_index = models.PositiveIntegerField(default=1, auto_created=True)
    level_started_at = models.DateTimeField(auto_now_add=True)
    is_paused = models.BooleanField(default=True, auto_created=True)
    paused_at = models.DateTimeField(null=True, auto_now_add=True)
    accumulated_pause_seconds = models.PositiveIntegerField(
        default=0,
        auto_created=True,
    )
    is_finished = models.BooleanField(default=False, auto_created=True)

    objects = BlindsTimerQuerySet.as_manager()

    class Meta:
        verbose_name = _("Blinds Timer")
        verbose_name_plural = _("Blinds Timers")

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    def get_current_level(self):
        s = self.start_level_index - 1  # Adjust for 0-indexed list
        levels = self.get_or_update_cached_levels()
        if self.is_finished:
            return s + 1, levels[s]

        elapsed = self.elapsed_seconds_since_start
        cumulative = 0

        for i in range(s, len(levels)):
            level = levels[i]
            cumulative += level.duration_seconds
            if elapsed < cumulative:
                break
        return i + 1, levels[i]

    @property
    def elapsed_seconds_since_start(self) -> int:
        now = timezone.now()
        elapsed = int((now - self.level_started_at).total_seconds())

        # If paused, deduct time since paused
        if self.is_paused and self.paused_at is not None:
            elapsed -= int((now - self.paused_at).total_seconds())

        # Deduct accumulated paused time (from previous pauses)
        elapsed -= self.accumulated_pause_seconds

        return max(0, elapsed)

    @property
    def max_level_index(self) -> int:
        return len(self.get_or_update_cached_levels())

    @property
    def can_decrement_level(self) -> bool:
        return self.start_level_index > 1

    @property
    def can_increment_level(self) -> bool:
        return self.start_level_index < self.max_level_index

    def move_start_level(self, level_index: int):
        if not self.is_finished and 1 <= level_index <= self.max_level_index:
            self.start_level_index = level_index
            self.level_started_at = timezone.now()
            self.accumulated_pause_seconds = 0
            self.is_paused = False
            self.paused_at = None
            self.save()

    def get_or_update_cached_levels(self):
        if not hasattr(self, "_cached_levels"):
            self.update_cached_levels()
        return self._cached_levels

    def update_cached_levels(self):
        self._cached_levels = list(self.levels.all())

    def pause(self):
        if not self.is_finished and not self.is_paused and self.paused_at is None:
            now = timezone.now()
            self.paused_at = now
            self.is_paused = True
            self.save()

    def resume(self):
        if not self.is_finished and self.is_paused and self.paused_at is not None:
            now = timezone.now()
            self.accumulated_pause_seconds += int(
                (now - self.paused_at).total_seconds(),
            )
            self.is_paused = False
            self.paused_at = None
            self.save()


class BlindsLevel(AbstractTimestampedModel):
    LEVEL_TYPE_PLAY = "play"
    LEVEL_TYPE_BREAK = "break"

    LEVEL_TYPE_CHOICES = [
        (LEVEL_TYPE_PLAY, "Play"),
        (LEVEL_TYPE_BREAK, "Break"),
    ]

    level_index = models.PositiveIntegerField()
    level_type = models.CharField(
        max_length=10,
        choices=LEVEL_TYPE_CHOICES,
    )
    duration_seconds = models.PositiveIntegerField()
    small_blind = models.PositiveIntegerField(null=True, blank=True)
    big_blind = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _("Blinds Level")
        verbose_name_plural = _("Blinds Levels")
        ordering = ["level_index"]
        abstract = True

    def __str__(self):
        return (
            f"{self.id} {self.level_index}. {self.level_type} for"
            f" {self.duration_seconds} seconds"
        )


class BlindsScheduleLevel(BlindsLevel):
    schedule = models.ForeignKey(
        BlindsSchedule,
        on_delete=models.CASCADE,
        related_name="levels",
        verbose_name=_("Blinds Schedule"),
    )

    class Meta:
        verbose_name = _("Blinds Schedule Level")
        verbose_name_plural = _("Blinds Schedule Levels")


class BlindsTimerLevel(BlindsLevel):
    timer = models.ForeignKey(
        BlindsTimer,
        on_delete=models.CASCADE,
        related_name="levels",
        verbose_name=_("Blinds Timer"),
    )

    class Meta:
        verbose_name = _("Blinds Timer Level")
        verbose_name_plural = _("Blinds Timer Levels")
