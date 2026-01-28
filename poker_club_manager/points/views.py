from types import SimpleNamespace

from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from poker_club_manager.common.models import Season
from poker_club_manager.common.utils.params import parse_int

from .filters import SeasonMemberListFilter


def leaderboard(request: HttpRequest, season_id: int | None = None):
    if season_id is not None:
        season = get_object_or_404(Season, id=season_id)
    else:
        season = Season.get_active_season()
        if not season:
            return render(
                request,
                "points/out_of_season.html",
            )

    search_query = request.GET.get("q", "").strip()
    order = request.GET.get("s", "points")

    members = SeasonMemberListFilter(
        search_query=search_query,
    ).apply(season)

    members_per_page = parse_int(
        request.GET.get("v"),
        default=20,
        minv=5,
        maxv=50,
    )

    paginator = Paginator(members, members_per_page)

    page = parse_int(
        request.GET.get("p"),
        default=1,
        minv=1,
        maxv=paginator.num_pages,
    )
    page_members = paginator.get_page(page)

    template = "points/leaderboard.html"
    if request.headers.get("HX-Request") == "true":
        template += "#leaderboard-table"

    return render(
        request,
        template,
        context={
            "members": page_members,
            "season": season,
            "page": page,
            "max_page": paginator.num_pages,
            "filters": {
                "order": order,
                "members_per_page": members_per_page,
                "search_query": search_query,
            },
            "archived": season.is_active is False,
        },
    )


def archive(request: HttpRequest):
    seasons = Season.objects.filter(is_active=False).order_by("-start_date")
    return render(
        request,
        "points/archive.html",
        {"seasons": seasons},
    )
