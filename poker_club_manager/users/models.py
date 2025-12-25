from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Case, Q, When
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class UserQuerySet(models.QuerySet):
    def filter_by_name(self, name_fragment: str) -> "UserQuerySet":
        """Filter users by matching name fragment, that matches the
        full name or username.

        Args:
            name_fragment (str): Fragment of name to match.

        Returns:
            UserQuerySet: Filtered queryset of users.

        """
        return (
            self.filter(
                Q(name__icontains=name_fragment) | Q(username__icontains=name_fragment),
            )
            .annotate(
                match_rank=Case(
                    When(username__iexact=name_fragment, then=0),
                    When(name__iexact=name_fragment, then=0),
                    When(username__istartswith=name_fragment, then=1),
                    When(name__istartswith=name_fragment, then=1),
                    When(username__icontains=name_fragment, then=2),
                    When(name__icontains=name_fragment, then=2),
                    default=3,
                    output_field=models.IntegerField(),
                ),
            )
            .order_by("match_rank", "username")
        )


class CustomUserManager(UserManager.from_queryset(UserQuerySet)):
    pass


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

    objects = CustomUserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
