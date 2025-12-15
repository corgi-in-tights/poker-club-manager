import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PointsConfig(AppConfig):
    name = "poker_club_manager.points"
    verbose_name = _("Points")

    def ready(self):
        with contextlib.suppress(ImportError):
            from . import signals  # noqa: F401, PLC0415
