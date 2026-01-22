# ruff: noqa: S311
import random
from datetime import timedelta
from types import SimpleNamespace

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

fake = Faker()

MODE_FIXED = "fixed"
MODE_CLEAR = "clear"


class Command(BaseCommand):
    help = "Seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            type=str,
            choices=[MODE_FIXED, MODE_CLEAR],
            default=MODE_FIXED,
            help="Mode: 'fixed' (create with fixed data), or 'clear' (only clear)",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=15,
            help="Number of records to create (only in random mode)",
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        count = options["count"]

        self.stdout.write(f"Seeding data in {mode} mode...")
        run_seed(self, mode, count)
        self.stdout.write(self.style.SUCCESS("Done."))


def clear_data(models):
    for name, model in vars(models).items():
        if name.lower() == "user":
            # Delete all users except superusers
            model.objects.exclude(is_superuser=True).delete()
        else:
            model.objects.all().delete()


def create_fixed_seasons(models):
    current_year = timezone.now().year
    seasons = []
    for i in range(3):
        start_year = current_year - i
        season = models.Season(
            name=f"{random.choice(['Fall', 'Winter'])} {start_year}",
            start_date=timezone.datetime(start_year, 1, 1).date(),
            end_date=timezone.datetime(start_year, 12, 31).date(),
            is_active=(i == 0),
        )
        seasons.append(season)
    return seasons


def create_random_users_memberships(models, count=20):
    users = []
    memberships = []

    for _ in range(count):
        u = models.User(username=fake.user_name(), email=fake.email(), name=fake.name())
        u.set_password("password123")
        users.append(u)
        m = models.SeasonMembership(
            user=u,
            season=random.choice(list(models.Season.objects.all())),
            points=random.randint(0, 200),
        )
        memberships.append(m)

    return [*users, *memberships]


def create_events(models, count=15):
    events = []

    for delta in [-10, -2, 0, 2, 10]:
        now = timezone.now()
        start_date = now + timedelta(days=delta)
        end_date = start_date + timedelta(hours=4)

        event = models.Event.objects.create(
            season=models.Season.get_active_season(),
            title=fake.sentence(),
            description=fake.text(max_nb_chars=random.randint(30, 200)),
            start_date=start_date,
            end_date=end_date,
            location="Building A, Room 1011",
        )
        events.append(event)

    for _ in range(count):
        start_date = fake.date_time_this_year(
            after_now=True,
            tzinfo=timezone.get_default_timezone(),
        )
        end_date = start_date + timedelta(hours=random.randint(2, 8))
        event = models.Event.objects.create(
            season=models.Season.get_active_season(),
            title=fake.sentence(),
            description=fake.text(max_nb_chars=random.randint(30, 200)),
            start_date=start_date,
            end_date=end_date,
            location=f"{fake.city()}, {fake.country()}",
        )
        events.append(event)

    return events


def run_seed(command, mode, count):
    """Seed database based on mode"""

    models = SimpleNamespace(
        Season=apps.get_model("common", "Season"),
        User=apps.get_model("users", "User"),
        SeasonMembership=apps.get_model("common", "SeasonMembership"),
        Event=apps.get_model("events", "Event"),
        BlindsScheduleLevel=apps.get_model("timers", "BlindsScheduleLevel"),
        BlindsSchedule=apps.get_model("timers", "BlindsSchedule"),
        BlindsTimerLevel=apps.get_model("timers", "BlindsTimerLevel"),
        BlindsTimer=apps.get_model("timers", "BlindsTimer"),
    )

    with transaction.atomic():
        if mode == MODE_CLEAR:
            clear_data(models)
            command.stdout.write("Cleared all data.")
            return

        if mode == MODE_FIXED:
            clear_data(models)
            command.stdout.write("Cleared all data before fixed initialization.")

            seed_factories = [
                ("Seasons", create_fixed_seasons, models),
                ("Users and Memberships", create_random_users_memberships, models),
                ("Events", create_events, models),
            ]

        for key, factory, *args in seed_factories:
            command.stdout.write(f"Creating {key}{'s' if key[-1] != 's' else ''}...")
            for obj in factory(*args) or []:
                obj.save()
                command.stdout.write(f"Created {key}: {obj!s}")
