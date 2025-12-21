from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class AbstractTimestampedModel(models.Model):
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True


class Season(AbstractTimestampedModel):
    name = models.CharField(_("Season Name"), max_length=255)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"), blank=True, null=True)
    active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"Season {self.id} | {self.name}"

    def get_membership_for_user(self, user: User):
        return SeasonMembership.objects.filter(user=user, season=self).first()


class SeasonMembership(AbstractTimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="season_memberships",
        verbose_name=_("User"),
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("Season"),
    )
    points = models.IntegerField(_("Points"), default=0)
    rebuys = models.PositiveIntegerField(_("Rebuys"), default=0)

    rebuys_stolen = models.PositiveIntegerField(_("Rebuys Stolen"), default=0)
    special_data = models.JSONField(_("Special Data"), default=dict, blank=True)

    class Meta:
        unique_together = ("user", "season")

    def __str__(self):
        return f"SeasonProfile {self.id} for User {self.user.username}"
