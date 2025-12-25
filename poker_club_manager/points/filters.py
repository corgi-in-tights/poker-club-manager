from dataclasses import dataclass

from poker_club_manager.common.models import Season, SeasonMembership


@dataclass(frozen=True)
class SeasonMemberListFilter:
    """
    Applies list-time filtering and ordering
    to Event querysets based on user intent.
    """

    search_query: str | None = None
    order: str = "points"

    def apply(self, season: Season):
        """
        Entry point used by views.
        """
        if season:
            qs = SeasonMembership.objects.filter(season=season)
        else:
            qs = SeasonMembership.objects.all()

        if self.search_query:
            qs = qs.search(self.search_query)

        return self._apply_order(qs)

    def _apply_order(self, qs):
        return qs.order_by("-points")
