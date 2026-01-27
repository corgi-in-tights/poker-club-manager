from django.urls import include, path

from poker_club_manager.events.views.event import (
    EventDetailView,
    check_in,
    check_into_first_active,
    create_event,
    list_events,
)
from poker_club_manager.events.views.manage import manage_event

from .partials import urlpatterns as partials_urlpatterns

app_name = "events"
urlpatterns = [
    path("", list_events, name="list"),
    path("partials/", include(partials_urlpatterns)),
    path("create/", create_event, name="create"),
    path("check-in/", check_into_first_active, name="check_into_first_active"),
    path("<int:event_id>/", EventDetailView.as_view(), name="detail"),
    path("<int:event_id>/check-in/", check_in, name="check_in"),
    path("<int:event_id>/manage/", manage_event, name="manage"),
]
