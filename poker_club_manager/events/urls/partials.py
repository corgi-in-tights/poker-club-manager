from django.urls import path

from poker_club_manager.events.views.manage import (
    add_guest,
    add_participant,
    eliminate_participant,
    manage_search_users,
    remove_guest,
    rsvp,
)

urlpatterns = [
    path(
        "<int:event_id>/manage/search-users/",
        manage_search_users,
        name="manage-search-users",
    ),
    path("<int:event_id>/rsvp/", rsvp, name="rsvp"),
    path(
        "<int:event_id>/manage/add-participant/",
        add_participant,
        name="add-participant",
    ),
    path(
        "<int:event_id>/manage/eliminate-participant/<int:participant_id>/",
        eliminate_participant,
        name="eliminate-participant",
    ),
    path(
        "<int:event_id>/manage/add-guest/",
        add_guest,
        name="add-guest",
    ),
    path(
        "<int:event_id>/manage/remove-guest/<int:guest_id>/",
        remove_guest,
        name="remove-guest",
    ),
]
