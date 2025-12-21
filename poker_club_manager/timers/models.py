from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel


class BlindsTemplateQuerySet(models.QuerySet):
    def global_or_owned(self, user_id):
        if user_id is None:
            return self.filter(is_global=True)
        return self.filter(
            Q(is_global=True) | Q(user__isnull=False, user_id=user_id),
        )


class BlindsTemplate(AbstractTimestampedModel):
    objects = BlindsTemplateQuerySet.as_manager()

    name = models.CharField(_("Name"), max_length=255)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="blinds_templates",
        verbose_name=_("User"),
        null=True,
        blank=True,
    )
    is_global = models.BooleanField(_("Is Global"), default=False)

    class Meta:
        verbose_name = _("Blinds Template")
        verbose_name_plural = _("Blinds Templates")

    def __str__(self):
        return self.name


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
    template = models.ForeignKey(
        BlindsTemplate,
        on_delete=models.CASCADE,
        related_name="levels",
        verbose_name=_("Blinds Template"),
    )
    duration_seconds = models.PositiveIntegerField()
    small_blind = models.PositiveIntegerField(null=True, blank=True)
    big_blind = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["level_index"]

    def __str__(self):
        return (
            f"{self.level_index}. {self.level_type} for {self.duration_seconds} seconds"
        )


class BlindsTimer(AbstractTimestampedModel):
    event = models.ForeignKey(
        "events.Event",
        related_name="timers",
        on_delete=models.CASCADE,
    )
    template = models.ForeignKey(
        BlindsTemplate,
        on_delete=models.PROTECT,
        related_name="timers",
    )

    current_level_index = models.PositiveIntegerField(default=0)
    level_started_at = models.DateTimeField(null=True, blank=True)

    is_paused = models.BooleanField(default=False)
    paused_at = models.DateTimeField(null=True, blank=True)
    accumulated_pause_seconds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Clock for Event {self.event.id}"

    @property
    def current_level(self):
        if self.is_finished:
            return None
        return list(self.template.levels.all())[self.current_level_index]

    @property
    def max_level_index(self) -> int:
        return self.template.levels.count() - 1

    @property
    def is_finished(self) -> bool:
        return self.max_level_index < self.current_level_index

    @property
    def remaining_seconds(self) -> int:
        if self.is_finished or self.is_paused or not self.level_started_at:
            return 0

        elapsed = int(
            (timezone.now() - self.level_started_at).total_seconds(),
        )

        elapsed += self.accumulated_pause_seconds
        duration = self.current_level.duration_seconds

        return max(0, duration - elapsed)

    @property
    def can_decrement_level(self) -> bool:
        return self.current_level_index > 0

    @property
    def can_increment_level(self) -> bool:
        return self.current_level_index < self.max_level_index

    def increment_level(self):
        if not self.is_finished and self.can_increment_level:
            self.current_level_index += 1
            self.level_started_at = timezone.now()
            self.accumulated_pause_seconds = 0
            self.is_paused = False
            self.paused_at = None
            self.save()

    def decrement_level(self):
        if self.can_decrement_level:
            self.current_level_index -= 1
            self.level_started_at = timezone.now()
            self.accumulated_pause_seconds = 0
            self.is_paused = False
            self.paused_at = None
            self.save()

    def pause(self):
        if not self.is_paused and self.paused_at is None:
            now = timezone.now()
            self.accumulated_pause_seconds += int(
                (now - self.level_started_at).total_seconds(),
            )
            self.paused_at = now
            self.is_paused = True

    def resume(self):
        if self.is_paused:
            self.is_paused = False
            self.paused_at = None
            self.save()
