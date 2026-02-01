import logging

from django.dispatch import receiver

from poker_club_manager.events.signals import event_completed

logger = logging.getLogger(__name__)


@receiver(event_completed)
def handle_event_completion(sender, event, **kwargs):
    for timer in event.timers.all():
        timer.finish()
    logger.info("All timers for event '%s' have been finished.", event.title)
