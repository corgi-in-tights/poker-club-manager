import logging

from django.db import models
from django.db.models import FilteredRelation, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel

logger = logging.getLogger(__name__)


class BlindsLevelChoices(models.TextChoices):
    PLAY = "play", _("Play")
    BREAK = "break", _("Break")


class BlindsLevel(AbstractTimestampedModel):
    level_index = models.PositiveIntegerField()
    level_type = models.CharField(
        max_length=10,
        choices=BlindsLevelChoices.choices,
        default=BlindsLevelChoices.PLAY,
    )
    duration_seconds = models.PositiveIntegerField()
    small_blind = models.PositiveIntegerField(null=True, blank=True)
    big_blind = models.PositiveIntegerField(null=True, blank=True)

    notes = models.TextField(blank=True)
    management_messages = models.JSONField(default=dict, blank=True)

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


class BlindTimerStates(models.TextChoices):
    RUNNING = "running", _("Running")
    PAUSED = "paused", _("Paused")
    FINISHED = "finished", _("Finished")


class BlindsTimerQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            Q(state=BlindTimerStates.RUNNING) | Q(state=BlindTimerStates.PAUSED),
        )

    def annotate_current_level(self):
        return self.annotate(
            current_level_relation=FilteredRelation(
                "levels",
                condition=Q(levels__level_index=models.F("current_level_index")),
            ),
        ).select_related("current_level_relation")


class BlindsTimer(AbstractTimestampedModel):
    name = models.CharField(_("Name"), max_length=255)
    event = models.ForeignKey(
        "events.Event",
        related_name="timers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    current_level_index = models.PositiveIntegerField(default=1, auto_created=True)
    current_level_started_at = models.DateTimeField(
        default=timezone.now,
    )
    state = models.CharField(
        max_length=50,
        choices=BlindTimerStates.choices,
        default=BlindTimerStates.RUNNING,
    )
    skipped_ms = models.FloatField(default=0.0)
    paused_at = models.DateTimeField(null=True, blank=True)

    objects = BlindsTimerQuerySet.as_manager()

    class Meta:
        verbose_name = _("Blinds Timer")
        verbose_name_plural = _("Blinds Timers")

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    @property
    def is_running(self) -> bool:
        return self.state == BlindTimerStates.RUNNING and self.paused_at is None

    @property
    def is_paused(self) -> bool:
        return self.state == BlindTimerStates.PAUSED and self.paused_at is not None

    @property
    def is_finished(self) -> bool:
        return self.state == BlindTimerStates.FINISHED

    @property
    def max_level_index(self) -> int:
        return len(self._get_or_set_cached_levels())

    @property
    def can_decrement_level(self) -> bool:
        return self.current_level_index > 1

    @property
    def can_increment_level(self) -> bool:
        return self.current_level_index < self.max_level_index

    @property
    def elapsed_ms(self) -> int:
        start = self.current_level_started_at
        now = timezone.now()
        return int((now - start).total_seconds() * 1000 - self.skipped_ms)

    def update(self) -> bool:
        # Timers not running or already finished do not update
        if self.is_finished or self.is_paused:
            return False

        current_level = self.get_current_level()
        # If the level is finished, move to the next level or finish the timer
        if self.elapsed_ms >= current_level.duration_seconds * 1000:
            if self.can_increment_level:
                self.set_current_level_index(self.current_level_index + 1)
            else:
                self.finish()
            return True
        return False

    def _get_or_set_cached_levels(self) -> list:
        if not hasattr(self, "_cached_levels"):
            self._update_cached_levels()
        return self._cached_levels

    def _update_cached_levels(self) -> None:
        self._cached_levels = list(self.levels.all().order_by("level_index"))
        # Invalidate current level cache
        self._cached_current_level = None

    def get_current_level(self) -> "BlindsLevel":
        return self._get_or_set_cached_levels()[self.current_level_index - 1]

    def set_current_level_index(self, new_level_index: int) -> bool:
        if self.is_finished:
            return False
        if new_level_index == self.current_level_index:
            return False
        if new_level_index < self.current_level_index and not self.can_decrement_level:
            return False
        if new_level_index > self.current_level_index and not self.can_increment_level:
            return False

        self.current_level_index = new_level_index
        self.restart_level()

        self._cached_current_level = None
        return True

    def restart_level(self) -> None:
        self.skipped_ms = 0
        self.state = BlindTimerStates.RUNNING
        self.paused_at = None
        self.current_level_started_at = timezone.now()
        self.save()

    def pause(self) -> None:
        if self.is_running:
            now = timezone.now()
            self.paused_at = now
            self.state = BlindTimerStates.PAUSED
            self.save()

    def resume(self) -> None:
        if self.is_paused:
            now = timezone.now()
            self.skipped_ms += int((now - self.paused_at).total_seconds() * 1000)
            self.state = BlindTimerStates.RUNNING
            self.paused_at = None
            self.save()

    def finish(self) -> None:
        if not self.is_finished:
            self.state = BlindTimerStates.FINISHED
            self.paused_at = None
            self.save()

    def get_remaining_time(self) -> tuple[int, int, int]:
        if self.is_finished:
            return 0, 0, 0

        elapsed_ms = self.elapsed_ms
        remainder_ms = max(
            0, self.get_current_level().duration_seconds * 1000 - elapsed_ms,
        )
        remainder_seconds = remainder_ms // 1000

        hours = remainder_seconds // 3600
        minutes = (remainder_seconds % 3600) // 60
        seconds = remainder_seconds % 60

        return hours, minutes, seconds


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
