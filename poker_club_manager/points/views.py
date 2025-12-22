from types import SimpleNamespace

from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from poker_club_manager.common.models import Season, SeasonMembership
from poker_club_manager.common.utils.params import parse_int

LEADERBOARD_DEFAULT_FILTERS = SimpleNamespace(
    {
        "members_per_page": 10,
    },
)


def active_leaderboard(request: HttpRequest):
    season = Season.get_active_season()
    if not season:
        return render(
            request,
            "points/out_of_season.html",
        )

    context = _build_leaderboard_context(
        request,
        season,
    )

    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "points/partials/leaderboard_table.html",
            context=context,
        )

    return render(
        request,
        "points/active_leaderboard.html",
        context,
    )


def archived_leaderboard(request: HttpRequest, season_id: int):
    season = get_object_or_404(Season, id=season_id, is_active=False)
    context = _build_leaderboard_context(
        request,
        season,
    )

    if request.headers.get("HX-Request") == "true":
        return render(
            request,
            "points/partials/leaderboard_table.html",
            context=context,
        )

    return render(
        request,
        "points/archived_leaderboard.html",
        context,
    )


def _build_leaderboard_context(request: HttpRequest, season: Season):
    members = SeasonMembership.objects.filter(season=season).ordered_by_points()

    search_query = request.GET.get("q", "").strip()
    if search_query:
        members = members.with_name_containing(search_query)

    members_per_page = parse_int(
        request.GET.get("v"),
        default=LEADERBOARD_DEFAULT_FILTERS.members_per_page,
        min_value=10,
        max_value=100,
    )
    paginator = Paginator(members, members_per_page)
    page_number = parse_int(
        request.GET.get("p"),
        default=1,
        min_value=1,
        max_value=paginator.num_pages,
    )

    return {
        "filters": SimpleNamespace(
            {
                "members_per_page": members_per_page,
            },
        ),
        "default_filters": LEADERBOARD_DEFAULT_FILTERS,
        "season": season,
        "members": paginator.page(page_number),
        "page": page_number,
        "max_page": paginator.num_pages,
    }


def archive(request: HttpRequest):
    seasons = Season.objects.filter(is_active=False).order_by("-start_date")
    return render(
        request,
        "points/archive.html",
        {"seasons": seasons},
    )
