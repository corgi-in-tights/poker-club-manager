from rest_framework import serializers

from poker_club_manager.events.models import (
    Event,
    EventRSVP,
    Participant,
)


class EventRSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRSVP
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


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            "id",
            "event",
            "user",
            "final_position",
        ]
        read_only_fields = ["event", "user"]


class EventSerializer(serializers.ModelSerializer):
    going_count = serializers.IntegerField(read_only=True)
    late_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = "__all__"
