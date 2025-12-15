import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlindsConfig(AppConfig):
    name = "poker_club_manager.blinds"
    verbose_name = _("Blinds")

    def ready(self):
        with contextlib.suppress(ImportError):
            from . import signals  # noqa: F401, PLC0415
