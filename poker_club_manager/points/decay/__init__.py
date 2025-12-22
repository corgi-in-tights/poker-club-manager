from poker_club_manager.points.scoring.base import DecayStrategy
from poker_club_manager.points.scoring.standard import GlobalAttendanceDecayStrategy

DEFAULT_STRATEGY = GlobalAttendanceDecayStrategy

DECAY_STRATEGY_MAP = {
    GlobalAttendanceDecayStrategy.key: GlobalAttendanceDecayStrategy,
}


def get_decay_strategy(strategy: str):
    return DECAY_STRATEGY_MAP.get(strategy, DEFAULT_STRATEGY)()


__all__ = [
    "DecayStrategy",
    "GlobalAttendanceDecayStrategy",
    "get_decay_strategy",
]
