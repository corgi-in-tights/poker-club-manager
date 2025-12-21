import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TimersConfig(AppConfig):
    name = "poker_club_manager.timers"
    verbose_name = _("Timers")

    def ready(self):
        with contextlib.suppress(ImportError):
            from . import signals  # noqa: F401, PLC0415
