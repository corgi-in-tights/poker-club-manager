from rest_framework.serializers import ModelSerializer

from poker_club_manager.timers.models import BlindsTimer


class BlindsTimerSerializer(ModelSerializer):
    class Meta:
        model = BlindsTimer
        fields = [
            "id",
            "name",
            "event",
            "start_level_index",
            "level_started_at",
            "is_paused",
            "accumulated_pause_seconds",
            "is_finished",
        ]

class BlindsTimerPollSerializer(ModelSerializer):
    class Meta:
        model = BlindsTimer
        fields = [
            "start_level_index",
            "level_started_at",
            "is_paused",
            "accumulated_pause_seconds",
            "is_finished",
        ]
