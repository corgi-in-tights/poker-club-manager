from .base import ScoringStrategy
from .bounty import BountyScoringStrategy
from .standard import BuyInDistributionScoringStrategy

DEFAULT_STRATEGY = BuyInDistributionScoringStrategy

STRATEGY_MAP = {
    BuyInDistributionScoringStrategy.key: BuyInDistributionScoringStrategy,
    BountyScoringStrategy.key: BountyScoringStrategy,
}


def get_scoring_strategy(strategy: str):
    return STRATEGY_MAP.get(strategy, DEFAULT_STRATEGY)()


__all__ = [
    "BountyScoringStrategy",
    "BuyInDistributionScoringStrategy",
    "ScoringStrategy",
    "get_scoring_strategy",
]
