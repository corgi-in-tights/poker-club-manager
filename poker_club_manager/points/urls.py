from django.urls import path

from . import views

app_name = "points"
urlpatterns = [
    path("", views.active_leaderboard, name="leaderboard"),
    path("archive/", views.archive, name="archive"),
    path(
        "archive/<int:season_id>/",
        views.archived_leaderboard,
        name="archived_leaderboard",
    ),
]
