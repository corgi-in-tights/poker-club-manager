from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import render

from poker_club_manager.common.models import Season, SeasonMembership


def leaderboard(request: HttpRequest, season_id: int | None = None):
    if season_id:
        season = Season.objects.get(id=season_id)
    else:
        season = Season.objects.get(is_active=True)

    if not season:
        return render(
            request,
            "points/leaderboard.html",
            {"season": None},
        )

    members = SeasonMembership.objects.filter(season=season)
    paged_members = Paginator(members, 50).page(request.GET.get("page", 1))

    return render(
        request,
        "points/leaderboard.html",
        {"season": season, "members": paged_members},
    )

def archive(request: HttpRequest):
    seasons = Season.objects.get(is_active=False).order_by("-start_date")
    paged_seasons = Paginator(seasons, 20).page(request.GET.get("page", 1))
    return render(
        request,
        "points/archive.html",
        {"seasons": paged_seasons},
    )
