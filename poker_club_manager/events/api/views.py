from django.db.models import Count, Q
from rest_framework import permissions, viewsets

from poker_club_manager.events.models import PokerEvent, PokerEventRSVP

from .serializers import (
    PokerEventAttendeeSerializer,
    PokerEventRSVPSerializer,
    PokerEventSerializer,
)


class PokerEventViewSet(viewsets.ModelViewSet):
    queryset = (
        PokerEvent.objects
        .annotate(
            going_count=Count(
                "rsvps",
                filter=Q(rsvps__status=PokerEventRSVP.GOING),
            ),
            late_count=Count(
                "rsvps",
                filter=Q(rsvps__status=PokerEventRSVP.LATE),
            ),
        )
    )
    serializer_class = PokerEventSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class PokerEventRSVPViewSet(viewsets.ModelViewSet):
    queryset = PokerEventRSVP.objects.all()
    serializer_class = PokerEventRSVPSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class PokerEventAttendeeViewSet(viewsets.ModelViewSet):
    queryset = PokerEventRSVP.objects.all()
    serializer_class = PokerEventAttendeeSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
