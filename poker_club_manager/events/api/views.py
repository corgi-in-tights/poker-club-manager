from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from poker_club_manager.common.api.permissions import CanHost
from poker_club_manager.events.models import Event, EventRSVP, Participant

from .serializers import (
    EventRSVPSerializer,
    EventSerializer,
    ParticipantSerializer,
)

User = get_user_model()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.annotate(
        going_count=Count(
            "rsvps",
            filter=Q(rsvps__status=EventRSVP.GOING),
        ),
        late_count=Count(
            "rsvps",
            filter=Q(rsvps__status=EventRSVP.LATE),
        ),
    )
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]

        if self.action in {"rsvp", "check_in"}:
            return [permissions.IsAuthenticated()]

        if self.action in {
            "add_user_attendee",
            "remove_user_attendee",
            "rank_user_attendee",
        }:
            return [CanHost()]

        return [permissions.IsAdminUser()]

    @action(detail=True, methods=["post"], url_path="rsvp")
    def rsvp(self, request, pk=None):
        event = self.get_object()
        event.rsvp_user(request.user,
                                 request.data.get("status", EventRSVP.GOING))
        return Response(
            {"status": "rsvp updated"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="add-user-attendee",
    )
    def add_user_attendee(self, request, pk=None):
        event = self.get_object()
        if "user_id" not in request.data:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data["user_id"]
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(
                {"error": "user not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        event.check_in_user(user)
        return Response(
            {"status": "check-in updated"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="remove-user-attendee",
    )
    def remove_user_attendee(self, request, pk=None):
        event = self.get_object()
        if "user_id" not in request.data:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request.data["user_id"]
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(
                {"error": "user not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        event.check_in_user(user)
        return Response(
            {"status": "check-in updated"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="check-in",
    )
    def check_in_user(self, request, pk=None):
        event = self.get_object()
        event.add_user_participant(request.user)
        return Response(
            {"status": "check-in updated"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="check-in-guest",
    )
    def check_in_guest(self, request, pk=None):
        event = self.get_object()
        if "guest_name" not in request.data or "guest_email" not in request.data:
            return Response(
                {"error": "guest_name and guest_email are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.add_guest_participant(
            request.user,
            guest_name=request.data["guest_name"],
            guest_email=request.data["guest_email"],
        )
        return Response(
            {"status": "check-in updated"},
            status=status.HTTP_200_OK,
        )


class EventRSVPViewSet(viewsets.ModelViewSet):
    queryset = EventRSVP.objects.all()
    serializer_class = EventRSVPSerializer
    permissions = [CanHost()]


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permissions = [CanHost()]
