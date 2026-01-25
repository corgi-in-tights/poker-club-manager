from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from poker_club_manager.timers.models import BlindsTimer

from .serializers import BlindsTimerPollSerializer


class TimerViewSet(viewsets.GenericViewSet):
    queryset = BlindsTimer.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def poll(self, request, pk=None):
        timer = self.get_object()
        # Lazy update the timer state before returning data
        # not the most scalable or secure but works for now
        # please don't hurt me for updating on a GET request
        timer.update()

        serializer = BlindsTimerPollSerializer(timer)
        return Response(serializer.data)
