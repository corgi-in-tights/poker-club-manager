from typing import TYPE_CHECKING

from .base import ScoringStrategy

if TYPE_CHECKING:
    from poker_club_manager.events.models import Event


class BountyScoringStrategy(ScoringStrategy):
    key = "bounty"

    POINTS_PER_BUY_IN = 3

    def calculate_points(
        self,
        total_participants: int,
        rank: int,
        eliminations: int,
    ) -> float:
        return round(eliminations * self.POINTS_PER_BUY_IN)

    def calculate(self, event: "Event") -> dict[int, int]:
        deltas = {}

        for p in event.participations.all():
            membership = p.season_membership
            if membership is None:
                continue

            # Award based on curve, eliminations then deduct buy-in points
            deltas[membership.id] = (
                self.calculate_points(event.total_participants, p.rank, p.eliminations)
            ) - self.POINTS_PER_BUY_IN

        return deltas
