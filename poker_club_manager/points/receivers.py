import logging

from django.conf import settings
from django.dispatch import receiver

from poker_club_manager.events.signals import event_completed

from .decay import get_decay_strategy
from .scoring import get_scoring_strategy
from .services import apply_scoring

logger = logging.getLogger(__name__)


@receiver(event_completed)
def handle_event_completion(sender, event, **kwargs):
    if not event.season:
        logger.info(
            "Event %s is not part of a season; skipping scoring.",
            event.id,
        )
        return
    if event.scoring_strategy.strip() == "":
        logger.info(
            "Event %s has no scoring strategy defined; skipping scoring.",
            event.id,
        )
        return

    logger.info(
        "Handling completion of event %s with scoring strategy %s",
        event.id,
        event.scoring_strategy,
    )
    strategy = get_scoring_strategy(event.scoring_strategy)

    if not strategy:
        msg = f"Unknown scoring strategy: {event.scoring_strategy}"
        raise ValueError(msg)

    deltas = strategy.calculate(event)
    logger.info(
        "Calculated deltas for event %s using strategy %s: %s",
        event.id,
        strategy.key,
        deltas,
    )

    apply_scoring(
        event,
        deltas,
        f"Event {event.id} point scoring using {strategy.key}",
    )

    # Apply global decay strategies
    # More inefficient to do it here but keeps the code simple
    # and not really built for scale (50000+) anyways
    decay_strategy = get_decay_strategy(settings.POINTS_DEFAULT_DECAY_STRATEGY)
    decay_deltas = decay_strategy.calculate(event)
    logger.info(
        "Calculated decay deltas for event %s using strategy %s",
        event.id,
        decay_strategy.key,
    )
    apply_scoring(
        event,
        decay_deltas,
        f"Event {event.id} decay using {decay_strategy.key}",
    )
