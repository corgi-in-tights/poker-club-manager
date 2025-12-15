import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "poker_club_manager.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import poker_club_manager.users.signals  # noqa: F401, PLC0415
