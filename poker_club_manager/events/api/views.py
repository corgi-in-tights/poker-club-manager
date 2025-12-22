from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from poker_club_manager.common.api.permissions import CanManageEvent
from poker_club_manager.events.models import Event, EventRSVP, Participant

from .serializers import (
    EventRSVPSerializer,
    EventSerializer,
    ParticipantSerializer,
)

User = get_user_model()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().annotate_rsvp_count()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in {"rsvp"}:
            return [permissions.IsAuthenticated()]
        return [CanManageEvent()]

    @action(detail=True, methods=["post"], url_path="rsvp")
    def rsvp(self, request, pk=None):
        event = self.get_object()
        event.rsvp_user(request.user, request.data.get("status", EventRSVP.GOING))
        return Response(
            {"status": "rsvp updated"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="add-participant",
    )
    def add_participant(self, request, pk=None):
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
        url_path="remove-participant",
    )
    def remove_participant(self, request, pk=None):
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


class EventRSVPViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventRSVP.objects.all()
    serializer_class = EventRSVPSerializer
    permission_classes = [CanManageEvent]


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [CanManageEvent]
