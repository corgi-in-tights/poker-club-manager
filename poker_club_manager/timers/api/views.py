from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.shortcuts import get_object_or_404
from rest_framework.views import APIView

from poker_club_manager.timers.models import BlindsTimer

from .serializers import BlindsTimerPollSerializer


class PollTimer(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def poll(self, request, timer_id: int) -> Response:
        timer = get_object_or_404(BlindsTimer, pk=timer_id)
        serializer = BlindsTimerPollSerializer(timer)
        return Response(serializer.data)
