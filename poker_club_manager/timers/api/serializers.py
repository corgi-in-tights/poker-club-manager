from rest_framework.serializers import (
    ModelSerializer,
    ReadOnlyField,
    SerializerMethodField,
)

from poker_club_manager.timers.models import (
    BlindsLevelChoices,
    BlindsTimer,
    BlindsTimerLevel,
)


class BlindsTimerLevelSerializer(ModelSerializer):
    started_at = ReadOnlyField()

    class Meta:
        model = BlindsTimerLevel
        fields = [
            "id",
            "level_index",
            "level_type",
            "started_at",
            "duration_seconds",
            "small_blind",
            "big_blind",
        ]

    def to_representation(self, instance):
        """Remove blind fields if the level is a break."""
        ret = super().to_representation(instance)
        if instance.level_type == BlindsLevelChoices.BREAK:
            ret.pop("small_blind", None)
            ret.pop("big_blind", None)
        return ret


class BlindsTimerPollSerializer(ModelSerializer):
    level = SerializerMethodField()

    class Meta:
        model = BlindsTimer
        fields = [
            "level",
            "state",
            "skipped_ms",
            "paused_at",
        ]
        read_only_fields = [
            "level",
            "state",
        ]

    def get_level(self, obj):
        level = obj.get_current_level()
        level.started_at = obj.current_level_started_at
        return BlindsTimerLevelSerializer(
            level,
        ).data


class BlindsTimerSerializer(ModelSerializer):
    class Meta:
        model = BlindsTimer
        fields = [
            "id",
            "name",
            "event",
            "current_level",
            "current_level_started_at",
            "state",
            "skipped_ms",
        ]
