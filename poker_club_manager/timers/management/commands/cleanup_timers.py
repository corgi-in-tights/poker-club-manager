from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Scans for running timers that have exceeded their duration"
        " and marks them as finished"
    )

    def handle(self, *args, **options):
        from poker_club_manager.timers.models import BlindsTimer  # noqa: PLC0415

        self.stdout.write(f"[{timezone.now()}] Starting timer cleanup...")

        # Call the method we built on your Custom Manager
        count = BlindsTimer.objects.cleanup_finished()

        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully finished {count} timer(s)."),
            )
        else:
            self.stdout.write("No timers required cleanup.")
