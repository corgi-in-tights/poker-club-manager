import logging
import math
from typing import TYPE_CHECKING

from .base import ScoringStrategy

if TYPE_CHECKING:
    from poker_club_manager.events.models import Event

logger = logging.getLogger(__name__)


# Not the most efficient but whatever
class BuyInDistributionScoringStrategy(ScoringStrategy):
    key = "buy_in_distribution"

    POINTS_PER_BUY_IN = 5

    def calculate_points(
        self,
        total: int,
        rank: int,
        alpha=1.25,
    ) -> int:
        if total < self.POINTS_PER_BUY_IN or rank < 1:
            return 0

        m = math.ceil(0.15 * total)
        if rank > m:
            return 0

        weights = [i**-alpha for i in range(1, m + 1)]
        z = sum(weights)

        t = self.POINTS_PER_BUY_IN * total
        return round(t * (rank**-alpha) / z)

    def calculate(self, event: "Event") -> dict[int, int]:
        deltas = {}
        total = event.get_total_participants()

        for p in event.participations.all():
            membership = p.season_membership
            if membership is None:
                continue
            rank = 0 if p.rank is None else p.rank
            # Award based on curve, eliminations then deduct buy-in points
            deltas[membership.id] = (
                self.calculate_points(total, rank) + p.eliminations
            ) - self.POINTS_PER_BUY_IN

        return deltas
