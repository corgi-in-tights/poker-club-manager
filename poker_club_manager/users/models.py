from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from poker_club_manager.common.models import AbstractTimestampedModel


class User(AbstractUser):
    """
    Default custom user model for Poker Club Manager.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    is_host_candidate = models.BooleanField(_("Is Host Candidate"), default=False)
    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

class SeasonProfile(AbstractTimestampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="season_profiles",
        verbose_name=_("User"),
    )
    season_name = models.CharField(_("Season Name"), max_length=255)
    points = models.IntegerField(_("Points"), default=0)

    def __str__(self):
        return f"SeasonProfile {self.id} for User {self.user.username}"

    class Meta:
        unique_together = ("user", "season_name")

