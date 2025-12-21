from rest_framework.routers import DefaultRouter

from .views import EventRSVPViewSet, EventViewSet, ParticipantViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"rsvps", EventRSVPViewSet, basename="rsvp")
router.register(r"attendees", ParticipantViewSet, basename="attendee")
