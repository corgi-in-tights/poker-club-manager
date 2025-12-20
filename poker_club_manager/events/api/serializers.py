from rest_framework import serializers

from poker_club_manager.events.models import (
    PokerEvent,
    PokerEventAttendee,
    PokerEventRSVP,
)


class PokerEventRSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerEventRSVP
        fields = [
            "id",
            "event",
            "user",
            "guest_name",
            "guest_email",
            "status",
            "updated_at",
        ]
        read_only_fields = ["event", "user"]


class PokerEventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerEventAttendee
        fields = [
            "id",
            "event",
            "user",
            "times_eliminated",
            "final_position",
            "points_earned",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user"]


class PokerEventSerializer(serializers.ModelSerializer):
    going_count = serializers.IntegerField(read_only=True)
    late_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PokerEvent
        fields = "__all__"
