from rest_framework.routers import DefaultRouter

from .views import PokerEventAttendeeViewSet, PokerEventRSVPViewSet, PokerEventViewSet

router = DefaultRouter()
router.register(r"events", PokerEventViewSet, basename="event")
router.register(r"rsvps", PokerEventRSVPViewSet, basename="rsvp")
router.register(r"attendees", PokerEventAttendeeViewSet, basename="attendee")
