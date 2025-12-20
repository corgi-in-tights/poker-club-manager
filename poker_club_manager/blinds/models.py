from django.db import models
from django.db.models import Q
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
        null=True, blank=True,
    )
    is_global = models.BooleanField(_("Is Global"), default=False)

    class Meta:
        verbose_name = _("Blinds Template")
        verbose_name_plural = _("Blinds Templates")

    def __str__(self):
        return self.name



class BlindsLevel(AbstractTimestampedModel):
    template = models.ForeignKey(
        BlindsTemplate,
        on_delete=models.CASCADE,
        related_name="levels",
        verbose_name=_("Blinds Template"),
    )
    level_number = models.PositiveIntegerField(_("Level Number"))
    small_blind = models.PositiveIntegerField(_("Small Blind"))
    big_blind = models.PositiveIntegerField(_("Big Blind"))
    duration_minutes = models.PositiveIntegerField(_("Duration (Minutes)"))

    class Meta:
        verbose_name = _("Blinds Level")
        verbose_name_plural = _("Blinds Levels")
        ordering = ["level_number"]

    def __str__(self):
        return (
            f"Level {self.level_number}: {self.small_blind}/{self.big_blind}"
            f" for {self.duration_minutes} minutes"
        )
