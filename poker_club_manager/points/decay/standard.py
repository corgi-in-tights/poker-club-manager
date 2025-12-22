from typing import TYPE_CHECKING

from .base import DecayStrategy

if TYPE_CHECKING:
    from poker_club_manager.events.models import Event


class GlobalAttendanceDecayStrategy(DecayStrategy):
    key = "global_attendance"

    def calculate_decay(self, total_participants: int, points: int) -> int:
        """
        Decay points based on global attendance.
        The more participants in the event, the higher the decay.
        """
        decay_rate = min(0.05, total_participants / 1000)  # Max 5% decay
        return round(points * decay_rate)

    def calculate(self, event: "Event") -> dict[int, int]:
        deltas = {}

        memberships = event.season.memberships.filter(points__gt=0)

        # After 100 points, each player is treated as the same
        for m in memberships:
            clamped_points = min(100, max(0, m.points))
            decayed_points = self.calculate_decay(
                event.total_participants,
                clamped_points,
            )
            deltas[m.id] = -decayed_points

        return deltas
