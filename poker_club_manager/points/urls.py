from django.urls import path

from . import views

app_name = "points"
urlpatterns = [
    path("", views.leaderboard, name="leaderboard"),
    path("archive/", views.archive, name="archive"),
    path("archive/<int:season_id>/", views.leaderboard, name="archived_leaderboard"),
]
